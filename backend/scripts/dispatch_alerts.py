"""
Dispatch all active alerts without running the web app.
Useful for cron/CI schedulers.
"""

import os
from backend import database as db
from backend.notifications import dispatch_alert


def main() -> None:
    alerts = db.get_all_active_alert_subscriptions()
    sent = 0
    for alert in alerts:
        result = dispatch_alert(alert)
        db.touch_alert_last_checked(alert["id"])
        sent += 1
        print(f"[ALERT] {alert.get('id')} {alert.get('scheme_name')} -> {result.get('message')}")
    print(f"[DONE] dispatched={sent}")


if __name__ == "__main__":
    # Example:
    # APP_TEST_MODE=0 python3 -m backend.scripts.dispatch_alerts
    main()
