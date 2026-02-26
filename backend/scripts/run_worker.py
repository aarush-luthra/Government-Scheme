"""Run RQ worker locally."""

from rq import Worker

from backend.worker.queue import get_redis_connection, DEFAULT_QUEUE_NAME


if __name__ == "__main__":
    connection = get_redis_connection()
    worker = Worker([DEFAULT_QUEUE_NAME], connection=connection)
    worker.work(with_scheduler=False)
