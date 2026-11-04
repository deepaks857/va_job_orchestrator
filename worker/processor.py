import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bson import ObjectId

from worker.config import worker_settings
from worker.db.mongodb import get_jobs_collection


def _download_video(url: str, dest: Path):
    response = httpx.get(url, follow_redirects=True, timeout=300, verify=False)
    response.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in response.iter_bytes(chunk_size=8192):
            f.write(chunk)


def _probe_video(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def _extract_video_stream(probe: dict) -> dict | None:
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    return None


def _parse_fps(avg_frame_rate: str) -> float:
    try:
        parts = avg_frame_rate.split("/")
        if len(parts) == 2:
            return float(parts[0]) / float(parts[1])
    except (ValueError, ZeroDivisionError):
        pass
    return 0.0


def _compute_video_metadata(probe: dict, file_size: int) -> dict:
    video_stream = _extract_video_stream(probe)
    fmt = probe.get("format", {})

    metadata = {
        "file_size_bytes": file_size,
        "duration_seconds": None,
        "width": None,
        "height": None,
        "codec": None,
        "fps": None,
        "frame_count": None,
        "bitrate_kbps": None,
    }

    duration = fmt.get("duration")
    if duration:
        metadata["duration_seconds"] = round(float(duration), 3)

    bitrate = fmt.get("bit_rate")
    if bitrate:
        metadata["bitrate_kbps"] = round(int(bitrate) / 1000)

    if video_stream:
        metadata["width"] = video_stream.get("width")
        metadata["height"] = video_stream.get("height")
        metadata["codec"] = video_stream.get("codec_name")

        avg_frame_rate = video_stream.get("avg_frame_rate", "")
        if avg_frame_rate:
            metadata["fps"] = round(_parse_fps(avg_frame_rate), 3)

        nb_frames = video_stream.get("nb_frames")
        if nb_frames:
            metadata["frame_count"] = int(nb_frames)
        elif metadata["duration_seconds"] and metadata["fps"]:
            metadata["frame_count"] = round(metadata["duration_seconds"] * metadata["fps"])

    return metadata


def _update_job_status(job_id: str, status: str, **extra):
    coll = get_jobs_collection()
    update = {"$set": {"status": status, **extra}}
    coll.update_one({"_id": ObjectId(job_id)}, update)


# def process_job(job_id: str, video_url: str):
def process_job(job_id: str, video_url: str="blahblah"):
    print(f"job_id: {job_id}, video_url:{video_url}")
    _update_job_status(job_id, "processing", started_at=datetime.now(timezone.utc))

    temp_dir = Path(worker_settings.download_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        dir=temp_dir, suffix=".mp4", delete=False
    ) as tmp:
        video_path = Path(tmp.name)

    try:
        _download_video(video_url, video_path)
        file_size = video_path.stat().st_size
        probe = _probe_video(video_path)
        metadata = _compute_video_metadata(probe, file_size)

        _update_job_status(
            job_id,
            "completed",
            result=metadata,
            completed_at=datetime.now(timezone.utc),
        )
    except Exception as e:
        _update_job_status(
            job_id,
            "failed",
            error=str(e),
            completed_at=datetime.now(timezone.utc),
        )
    finally:
        if video_path.exists():
            os.unlink(video_path)
