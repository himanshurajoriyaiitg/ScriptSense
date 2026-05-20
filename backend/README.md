# ScriptSense Backend

Backend service for the GradeOps / ScriptSense problem statement: bulk handwritten exam intake, rubric-driven grading, human-in-the-loop review, and plagiarism flagging.

## What This Backend Does

- Auth with `instructor` and `ta` roles
- Rubric creation and retrieval
- Single and bulk PDF upload
- OCR extraction pipeline
- AI or heuristic grading
- Regrading with linked rubric snapshots
- Human review queue with approve/override flow
- Plagiarism similarity flags
- Processing jobs and pipeline traces
- Page-image artifacts for review dashboards

## Main Backend Flows

### 1. Instructor setup

- `POST /signup`
- `POST /login`
- `POST /rubrics`

### 2. Submission processing

- `POST /upload`
- `POST /upload/bulk`
- `GET /jobs`
- `GET /jobs/{job_id}`

### 3. Review workflow

- `GET /review-queue`
- `GET /review-queue/next`
- `GET /files`
- `GET /files/{file_id}`
- `GET /files/{file_id}/artifacts`
- `GET /files/{file_id}/pipeline`
- `PATCH /files/{file_id}/review`

### 4. Quality checks

- `GET /plagiarism/flags`
- `GET /stats`
- `GET /health`

## Project Structure

- `app/routes/`: API endpoints
- `app/services/`: OCR, grading, plagiarism, jobs, storage, and artifacts
- `app/models/`: SQLAlchemy models
- `app/schemas/`: request and response contracts
- `tests/`: API tests

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
./venv/bin/pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in real values.
4. Make sure PostgreSQL is available if you use the default example `DATABASE_URL`.
5. Install `tesseract` locally if you want real OCR outside Docker.

## Run Locally

```bash
./venv/bin/uvicorn app.main:app --reload
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Run Tests

```bash
./venv/bin/python -m pytest tests -q
```

## Docker

Build:

```bash
docker build -t scriptsense-backend .
```

Run:

```bash
docker run -p 8000:8000 --env-file .env scriptsense-backend
```

## PS Readiness Notes

This backend now covers most of the backend-side PS expectations:

- bulk scan upload
- rubric-driven grading
- instructor vs TA access
- OCR processing
- HITL review workflow
- plagiarism similarity flags
- review assets for dashboard-style UI
- pipeline/job visibility

Remaining future upgrades for a production-grade version:

- Alembic migrations
- real async worker queue such as Celery/RQ
- cloud storage such as S3/GCS
- handwritten-specialized VLM/OCR integration
- true answer-region cropping instead of page-level review artifacts
