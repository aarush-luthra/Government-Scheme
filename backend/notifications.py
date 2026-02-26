"""Notification utilities for multi-provider push delivery.

Primary provider: FCM (web token)
Fallback provider: WebPush (VAPID)
"""

import json
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from typing import Any, Dict, List, Optional

import requests

from backend import database as db

try:
    from pywebpush import webpush, WebPushException
except Exception:  # pragma: no cover - optional dependency fallback
    webpush = None

    class WebPushException(Exception):
        pass


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "user_data", "notification_logs")
os.makedirs(LOG_DIR, exist_ok=True)


def _append_log(entry: Dict[str, Any]) -> None:
    date_key = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(LOG_DIR, f"{date_key}.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def send_email(subject: str, body: str, to_email: str) -> Dict[str, Any]:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    sender = os.getenv("SMTP_SENDER", username).strip()

    if not (host and username and password and to_email):
        return {"success": False, "provider": "email", "message": "SMTP not configured"}

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)

    return {"success": True, "provider": "email", "message": "Email sent"}


def _send_fcm(token: str, title: str, message: str) -> Dict[str, Any]:
    server_key = os.getenv("FCM_SERVER_KEY", "").strip()
    if not server_key:
        return {"success": False, "provider": "fcm", "message": "FCM not configured"}

    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": message,
        },
        "data": {
            "title": title,
            "body": message,
        },
    }
    resp = requests.post("https://fcm.googleapis.com/fcm/send", json=payload, headers=headers, timeout=10)
    if resp.ok:
        return {"success": True, "provider": "fcm", "message": "FCM sent", "raw": resp.json()}
    return {"success": False, "provider": "fcm", "message": f"FCM failed ({resp.status_code})", "raw": resp.text}


def _send_webpush(subscription: Dict[str, Any], title: str, message: str) -> Dict[str, Any]:
    if webpush is None:
        return {"success": False, "provider": "webpush", "message": "pywebpush not installed"}

    vapid_private_key = os.getenv("VAPID_PRIVATE_KEY", "").strip()
    vapid_claims_sub = os.getenv("VAPID_CLAIMS_SUB", "mailto:admin@example.com").strip()
    endpoint = subscription.get("endpoint")
    p256dh = subscription.get("p256dh")
    auth = subscription.get("auth")
    if not (vapid_private_key and endpoint and p256dh and auth):
        return {"success": False, "provider": "webpush", "message": "WebPush not configured"}

    payload = json.dumps({"title": title, "body": message}, ensure_ascii=False)
    try:
        webpush(
            subscription_info={
                "endpoint": endpoint,
                "keys": {"p256dh": p256dh, "auth": auth},
            },
            data=payload,
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": vapid_claims_sub},
            ttl=120,
        )
        return {"success": True, "provider": "webpush", "message": "WebPush sent"}
    except WebPushException as exc:
        return {"success": False, "provider": "webpush", "message": f"WebPush failed: {exc}"}


def send_push_for_user(user_id: str, title: str, message: str) -> Dict[str, Any]:
    subscriptions = db.get_push_subscriptions(user_id)
    if not subscriptions:
        return {"success": False, "provider": "push", "message": "No active push subscriptions"}

    attempts: List[Dict[str, Any]] = []
    delivered = False
    for subscription in subscriptions:
        result: Dict[str, Any]
        if subscription.get("provider") == "fcm" and subscription.get("fcm_token"):
            result = _send_fcm(subscription["fcm_token"], title, message)
            attempts.append({"subscription_id": subscription["id"], **result})
            delivered = delivered or result.get("success", False)
            if result.get("success"):
                continue
            # fallback to webpush only if keys available
            if subscription.get("endpoint") and subscription.get("p256dh") and subscription.get("auth"):
                fallback = _send_webpush(subscription, title, message)
                attempts.append({"subscription_id": subscription["id"], "fallback": True, **fallback})
                delivered = delivered or fallback.get("success", False)
        else:
            result = _send_webpush(subscription, title, message)
            attempts.append({"subscription_id": subscription["id"], **result})
            delivered = delivered or result.get("success", False)

    summary = {
        "success": delivered,
        "provider": "push",
        "message": "Push delivered" if delivered else "Push failed for all subscriptions",
        "attempts": attempts,
    }
    _append_log({"event": "push_delivery", "user_id": user_id, "title": title, "message": message, "summary": summary, "timestamp": datetime.now().isoformat()})
    return summary


def dispatch_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
    channel = str(alert.get("channel") or "in_app").lower()
    scheme = str(alert.get("scheme_name") or "Scheme")
    deadline = str(alert.get("next_deadline") or "No deadline provided")
    user_id = str(alert.get("user_id") or "")
    title = f"Scheme alert: {scheme}"
    body = f"Reminder: {scheme}\nDeadline: {deadline}\nLast checked: {alert.get('last_checked') or 'N/A'}"

    if channel == "email":
        result = send_email(subject=title, body=body, to_email=str(alert.get("contact") or "").strip())
    elif channel == "push":
        # Real push path with provider fallback.
        result = send_push_for_user(user_id=user_id, title=title, message=body)
    else:
        result = {"success": True, "provider": "in_app", "message": "In-app notification available"}

    if user_id:
        db.add_notification_event(
            user_id=user_id,
            alert_id=alert.get("id"),
            scheme_name=scheme,
            title=title,
            body=body,
            channel=channel,
        )
    db.log_alert_delivery_attempt(
        channel=channel,
        success=bool(result.get("success")),
        user_id=user_id or None,
        alert_id=alert.get("id"),
        provider=result.get("provider"),
    )

    _append_log(
        {
            "event": "dispatch_alert",
            "channel": channel,
            "scheme_name": scheme,
            "contact": alert.get("contact"),
            "user_id": user_id,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    )
    return result
