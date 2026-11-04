from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient | None = None


async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.mongodb_uri)


async def close_db():
    global client
    if client:
        client.close()
        client = None


def get_db():
    if client is None:
        raise RuntimeError("Database not initialized")
    return client[settings.mongodb_db]


def get_jobs_collection():
    return get_db()["jobs"]
