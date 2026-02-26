"""Background tasks for alerts and status polling."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from backend import database as db
from backend.notifications import dispatch_alert

logger = logging.getLogger(__name__)

STATUS_API_BASE = os.getenv("SCHEME_STATUS_API_BASE", "").strip()
MAX_RETRIES = int(os.getenv("WORKER_MAX_RETRIES", "3"))


def _status_from_remote(scheme_name: str) -> str:
    # Configurable external polling contract:
    # GET {SCHEME_STATUS_API_BASE}?scheme_name=...
    # -> {"status": "approved|under_review|rejected|pending"}
    if not STATUS_API_BASE:
        # deterministic fallback when external API is not configured
        lower = scheme_name.lower()
        if "kisan" in lower:
            return "under_review"
        if "pension" in lower:
            return "approved"
        return "pending"
    response = requests.get(STATUS_API_BASE, params={"scheme_name": scheme_name}, timeout=10)
    response.raise_for_status()
    payload = response.json() if response.content else {}
    return str(payload.get("status") or "pending")


def _should_dispatch_deadline(next_deadline: Optional[str]) -> bool:
    if not next_deadline:
        return False
    try:
        due = datetime.fromisoformat(next_deadline)
    except ValueError:
        return False
    now = datetime.now()
    return 0 <= (due - now).days <= 2


def _log_failure(task_name: str, payload: Dict[str, Any], exc: Exception, retries: int = 0, dead_letter: bool = False) -> None:
    logger.error("Task %s failed retries=%s dead_letter=%s payload=%s err=%s", task_name, retries, dead_letter, payload, exc)
    db.log_task_failure(
        task_name=task_name,
        payload=payload,
        error_message=str(exc),
        retries=retries,
        is_dead_letter=dead_letter,
    )


def process_deadline_alerts(user_id: Optional[str] = None, retries: int = 0) -> Dict[str, Any]:
    """Dispatch alerts close to deadlines."""
    try:
        if user_id:
            alerts = db.get_alert_subscriptions(user_id)
        else:
            alerts = db.get_all_active_alert_subscriptions()
        sent = []
        for alert in alerts:
            if not alert.get("is_active"):
                continue
            if not _should_dispatch_deadline(alert.get("next_deadline")):
                continue
            result = dispatch_alert(alert)
            db.touch_alert_last_checked(alert["id"])
            sent.append({"alert_id": alert["id"], "result": result})
        logger.info("process_deadline_alerts sent=%s", len(sent))
        return {"success": True, "sent": len(sent), "items": sent}
    except Exception as exc:
        if retries < MAX_RETRIES:
            return process_deadline_alerts(user_id=user_id, retries=retries + 1)
        _log_failure("process_deadline_alerts", {"user_id": user_id}, exc, retries=retries, dead_letter=True)
        return {"success": False, "error": str(exc), "dead_letter": True}


def poll_scheme_statuses(user_id: Optional[str] = None, retries: int = 0) -> Dict[str, Any]:
    """Poll external scheme status API and notify users when statuses change."""
    try:
        rows = db.get_saved_schemes(user_id) if user_id else db.get_all_saved_schemes()
        updated = 0
        for row in rows:
            uid = row["user_id"] if row.get("user_id") else user_id
            if not uid:
                continue
            current = str(row.get("application_status") or "pending")
            latest = _status_from_remote(str(row.get("scheme_name") or ""))
            db.update_saved_scheme_status(uid, row["scheme_name"], latest)
            if latest != current:
                updated += 1
                db.add_notification_event(
                    user_id=uid,
                    scheme_name=row["scheme_name"],
                    title=f"Status changed: {row['scheme_name']}",
                    body=f"Application status updated from '{current}' to '{latest}'.",
                    channel="in_app",
                )
        logger.info("poll_scheme_statuses updated=%s", updated)
        return {"success": True, "updated": updated}
    except Exception as exc:
        if retries < MAX_RETRIES:
            return poll_scheme_statuses(user_id=user_id, retries=retries + 1)
        _log_failure("poll_scheme_statuses", {"user_id": user_id}, exc, retries=retries, dead_letter=True)
        return {"success": False, "error": str(exc), "dead_letter": True}
