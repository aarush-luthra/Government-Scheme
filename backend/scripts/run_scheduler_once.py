"""Enqueue scheduled jobs once."""

from backend.worker.queue import get_queue
from backend.worker.scheduler import enqueue_scheduled_jobs


if __name__ == "__main__":
    queue = get_queue()
    result = enqueue_scheduled_jobs(queue)
    print(result)
