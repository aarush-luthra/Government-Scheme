from backend.worker.scheduler import enqueue_scheduled_jobs


class _DummyJob:
    def __init__(self, idx):
        self.id = f"job-{idx}"


class _DummyQueue:
    def __init__(self):
        self.calls = []

    def enqueue(self, fn, **kwargs):
        self.calls.append((fn.__name__, kwargs))
        return _DummyJob(len(self.calls))


def test_enqueue_scheduled_jobs_enqueues_alert_and_poll():
    queue = _DummyQueue()
    result = enqueue_scheduled_jobs(queue)

    assert "alert_job_id" in result
    assert "status_job_id" in result
    names = [name for name, _ in queue.calls]
    assert "process_deadline_alerts" in names
    assert "poll_scheme_statuses" in names
