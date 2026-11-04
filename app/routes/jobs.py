from datetime import datetime, timezone
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from app.db.mongodb import get_jobs_collection
from app.models.schemas import JobCreate, JobResponse, VideoResult
from app.tasks.queue import enqueue_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _serialize_job(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.post("", status_code=201)
async def create_job(body: JobCreate):
    coll = get_jobs_collection()
    now = datetime.now(timezone.utc)
    print(f"recvd body {body}")
    print(f"of type {type(body)}")
    doc = {
        "video_url": str(body.video_url),
        "status": "queued",
        "result": None,
        "error": None,
        "created_at": now,
        "started_at": None,
        "completed_at": None,
    }
    print(f" doc {doc}")
    result = await coll.insert_one(doc)
    job_id = str(result.inserted_id)
    print(f" enqueuing for job_id {job_id}")
    enqueue_job(job_id, str(body.video_url))
    created = await coll.find_one({"_id": result.inserted_id})
    return JobResponse(**_serialize_job(created))


@router.get("")
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
):
    coll = get_jobs_collection()
    query = {}
    if status:
        query["status"] = status
    cursor = coll.find(query).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    total = await coll.count_documents(query)
    jobs = [JobResponse(**_serialize_job(d)) for d in docs]
    return {"jobs": jobs, "total": total}


@router.get("/{job_id}")
async def get_job(job_id: str):
    coll = get_jobs_collection()
    if not ObjectId.is_valid(job_id):
        raise HTTPException(400, "Invalid job ID")
    doc = await coll.find_one({"_id": ObjectId(job_id)})
    if not doc:
        raise HTTPException(404, "Job not found")
    return JobResponse(**_serialize_job(doc))


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str):
    coll = get_jobs_collection()
    if not ObjectId.is_valid(job_id):
        raise HTTPException(400, "Invalid job ID")
    result = await coll.delete_one({"_id": ObjectId(job_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Job not found")
