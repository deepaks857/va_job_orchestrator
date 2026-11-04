from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class VideoResult(BaseModel):
    frame_count: int | None = None
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    codec: str | None = None
    fps: float | None = None
    bitrate_kbps: int | None = None
    file_size_bytes: int | None = None


class JobCreate(BaseModel):
    video_url: HttpUrl


class JobResponse(BaseModel):
    id: str = Field(alias="_id")
    video_url: str
    status: JobStatus
    result: VideoResult | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"populate_by_name": True, "from_attributes": True}


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int


class HealthResponse(BaseModel):
    status: str
    mongodb: str
    redis: str
