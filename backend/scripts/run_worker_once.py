"""Enqueue scheduled jobs and process once in burst mode for local verification."""

from rq import Worker

from backend.worker.queue import get_queue, get_redis_connection, DEFAULT_QUEUE_NAME
from backend.worker.scheduler import enqueue_scheduled_jobs


if __name__ == "__main__":
    queue = get_queue()
    print("[scheduler] enqueueing jobs...")
    print(enqueue_scheduled_jobs(queue))

    print("[worker] starting burst worker...")
    worker = Worker([DEFAULT_QUEUE_NAME], connection=get_redis_connection())
    worker.work(burst=True)
    print("[worker] completed burst execution")
