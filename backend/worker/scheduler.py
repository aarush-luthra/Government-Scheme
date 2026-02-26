"""Simple scheduler utilities for enqueueing periodic jobs."""

from datetime import datetime
from typing import Dict

from rq import Queue
from rq.job import Retry

from backend.worker.tasks import process_deadline_alerts, poll_scheme_statuses


def enqueue_scheduled_jobs(queue: Queue, now: datetime | None = None) -> Dict[str, str]:
    current = now or datetime.now()
    # Deadline alerts every 30 minutes and status polling hourly.
    alert_job = queue.enqueue(process_deadline_alerts, retry=Retry(max=2, interval=[5, 15]))
    status_job = queue.enqueue(poll_scheme_statuses, retry=Retry(max=2, interval=[5, 15]))
    return {
        "enqueued_at": current.isoformat(),
        "alert_job_id": alert_job.id,
        "status_job_id": status_job.id,
    }
