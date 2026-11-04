import redis
from rq import Queue

from app.config import settings

_redis_client: redis.Redis | None = None
_queue: Queue | None = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_uri)
    return _redis_client


def get_queue() -> Queue:
    global _queue
    if _queue is None:
        _queue = Queue("default", connection=get_redis())
    return _queue


def enqueue_job(job_id: str, video_url: str):
    from worker.processor import process_job

    q = get_queue()
    q.enqueue(process_job, job_id, video_url)
