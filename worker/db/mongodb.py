from pymongo import MongoClient
from worker.config import worker_settings

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(worker_settings.mongodb_uri)
    return _client


def get_db():
    return get_client()[worker_settings.mongodb_db]


def get_jobs_collection():
    return get_db()["jobs"]


def close_client():
    global _client
    if _client:
        _client.close()
        _client = None
