from datetime import datetime, timezone
from typing import Any

from app.core.config import PIPELINE_NAME
from app.models.job_model import ProcessingJob
from app.services.rubric_service import deserialize_json_payload, serialize_json_payload


def create_processing_job(
    db,
    *,
    requested_by_id: int | None,
    job_type: str,
    total_files: int,
    rubric_id: int | None = None,
    message: str | None = None,
) -> ProcessingJob:
    job = ProcessingJob(
        requested_by_id=requested_by_id,
        job_type=job_type,
        total_files=total_files,
        rubric_id=rubric_id,
        message=message,
        pipeline_name=PIPELINE_NAME,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_processing_job_counts(
    db,
    job: ProcessingJob,
    *,
    processed_increment: int = 0,
    failed_increment: int = 0,
) -> ProcessingJob:
    job.processed_files += processed_increment
    job.failed_files += failed_increment
    db.commit()
    db.refresh(job)
    return job


def finalize_processing_job(
    db,
    job: ProcessingJob,
    *,
    summary: dict[str, Any] | None = None,
) -> ProcessingJob:
    job.finished_at = datetime.now(timezone.utc)
    if job.failed_files and job.processed_files:
        job.status = "completed_with_errors"
    elif job.failed_files and not job.processed_files:
        job.status = "failed"
    else:
        job.status = "completed"

    if summary is not None:
        job.result_summary = serialize_json_payload(summary)

    db.commit()
    db.refresh(job)
    return job


def build_job_summary(job: ProcessingJob) -> dict[str, Any]:
    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "pipeline_name": job.pipeline_name,
        "requested_by_id": job.requested_by_id,
        "rubric_id": job.rubric_id,
        "total_files": job.total_files,
        "processed_files": job.processed_files,
        "failed_files": job.failed_files,
        "message": job.message,
        "result_summary": deserialize_json_payload(job.result_summary),
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
