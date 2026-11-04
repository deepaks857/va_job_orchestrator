from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db.mongodb import connect_db, close_db
from app.routes.jobs import router as jobs_router
from app.tasks.queue import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Video Analytics Job Orchestrator",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(jobs_router)


@app.get("/health")
async def health():
    statuses = {"status": "ok", "mongodb": "unknown", "redis": "unknown"}

    try:
        from app.db.mongodb import get_db
        await get_db().command("ping")
        statuses["mongodb"] = "connected"
    except Exception:
        statuses["mongodb"] = "disconnected"
        statuses["status"] = "degraded"

    try:
        r = get_redis()
        r.ping()
        statuses["redis"] = "connected"
    except Exception:
        statuses["redis"] = "disconnected"
        statuses["status"] = "degraded"

    return statuses
