from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth import require_roles
from app.models.job_model import ProcessingJob
from app.models.user_model import User
from app.schemas.api import ProcessingJobResponse, UserRole
from app.services.job_service import build_job_summary

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=list[ProcessingJobResponse])
async def list_jobs(
    limit: int = 50,
    status_filter: str | None = None,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    query = db.query(ProcessingJob)
    if status_filter:
        query = query.filter(ProcessingJob.status == status_filter)

    jobs = (
        query.order_by(ProcessingJob.created_at.desc(), ProcessingJob.id.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return [build_job_summary(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=ProcessingJobResponse)
async def get_job(
    job_id: int,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing job not found",
        )

    return build_job_summary(job)
