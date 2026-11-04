# va_job_orchestrator

## Architecture Overview
```
User ──▶ FastAPI ──▶ Redis Queue ──▶ Worker ──▶ ffmpeg
           │                              │
           ▼                              ▼
       ┌─────────────────────────────────────┐
       │              MongoDB                │
       │  (jobs with status & result)        │
       └─────────────────────────────────────┘

```

## Key Design Decisions
- **FastAPI** with `motor` (async MongoDB driver) (for non-blocking handling) and `redis-py` + `rq` (Redis Queue)
- **Worker** uses `rq` worker, `pymongo` (sync) for procedural clarity, `ffmpeg-python` or raw subprocess for ffprobe
- **Redis** as the pub/sub message broker (simple, lightweight, no extra infra)
- **Docker Compose** for local dev (api, worker, mongo, redis)
- **Kubernetes manifests** (not Helm, to keep it simple) for deploying to Minikube
- **Terraform** deploys Minikube and applies K8s manifests

## Quickstart
```bash
# Local dev
docker compose -f docker/docker-compose.yml up

# Test API
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://example.com/video.mp4"}'

curl http://localhost:8000/jobs

# K8s
kubectl apply -f k8s/namespace.yaml -f k8s/configmap.yaml
kubectl apply -f k8s/mongodb/ -f k8s/redis/
kubectl apply -f k8s/api/ -f k8s/worker/

# Terraform
cd terraform && terraform init && terraform apply
