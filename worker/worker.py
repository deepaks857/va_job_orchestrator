import redis
from rq import Worker, Queue

from worker.config import worker_settings

redis_conn = redis.from_url(worker_settings.redis_uri)
queue = Queue("default", connection=redis_conn)

if __name__ == "__main__":
    worker = Worker([queue], connection=redis_conn)
    worker.work()
