from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import PLAGIARISM_THRESHOLD
from app.database.db import get_db
from app.dependencies.auth import require_roles
from app.models.artifact_model import SubmissionArtifact
from app.models.file_model import UploadedFile
from app.models.rubric_model import GradingRubric
from app.models.user_model import User
from app.schemas.api import (
    ArtifactListResponse,
    FileReviewRequest,
    PipelineTraceResponse,
    PlagiarismFlagResponse,
    ReviewQueueResponse,
    ReviewResponse,
    StatsResponse,
    UploadedFileDetail,
    UploadedFileSummary,
    UserRole,
)
from app.services.pdf_service import (
    build_file_detail,
    build_file_summary,
    serialize_grading_result,
)
from app.services.artifact_service import build_artifact_summary
from app.services.plagiarism_service import update_ai_confidence

router = APIRouter(tags=["dashboard"])


@router.get("/files", response_model=list[UploadedFileSummary])
async def get_all_files(
    status_filter: str | None = None,
    review_status_filter: str | None = None,
    rubric_id: int | None = None,
    exam_name: str | None = None,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    query = db.query(UploadedFile)
    if status_filter:
        query = query.filter(UploadedFile.status == status_filter)
    if review_status_filter:
        query = query.filter(UploadedFile.review_status == review_status_filter)
    if rubric_id is not None:
        query = query.filter(UploadedFile.rubric_id == rubric_id)
    if exam_name:
        query = query.filter(UploadedFile.exam_name == exam_name)

    files = query.order_by(UploadedFile.created_at.desc(), UploadedFile.id.desc()).all()
    return [build_file_summary(file) for file in files]


@router.get("/files/{file_id}", response_model=UploadedFileDetail)
async def get_file_detail(
    file_id: int,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded file not found",
        )

    return build_file_detail(file_record)


@router.get("/files/{file_id}/artifacts", response_model=ArtifactListResponse)
async def get_file_artifacts(
    file_id: int,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded file not found",
        )

    artifacts = (
        db.query(SubmissionArtifact)
        .filter(SubmissionArtifact.file_id == file_id)
        .order_by(SubmissionArtifact.page_number.asc(), SubmissionArtifact.id.asc())
        .all()
    )
    summaries = [build_artifact_summary(artifact) for artifact in artifacts]

    return {
        "file_id": file_id,
        "count": len(summaries),
        "artifacts": summaries,
    }


@router.get("/artifacts/{artifact_id}")
async def get_artifact_file(
    artifact_id: int,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    artifact = db.query(SubmissionArtifact).filter(SubmissionArtifact.id == artifact_id).first()
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )

    return FileResponse(
        artifact.local_path,
        media_type=artifact.content_type,
        filename=artifact.storage_key.split("/")[-1],
    )


@router.get("/files/{file_id}/pipeline", response_model=PipelineTraceResponse)
async def get_pipeline_trace(
    file_id: int,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded file not found",
        )

    file_detail = build_file_detail(file_record)
    return {
        "file_id": file_id,
        "pipeline_trace": file_detail["pipeline_trace"],
    }


@router.get("/review-queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    limit: int = 50,
    only_pending: bool = True,
    rubric_id: int | None = None,
    exam_name: str | None = None,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    query = db.query(UploadedFile)
    if only_pending:
        query = query.filter(UploadedFile.review_status == "pending")
    if rubric_id is not None:
        query = query.filter(UploadedFile.rubric_id == rubric_id)
    if exam_name:
        query = query.filter(UploadedFile.exam_name == exam_name)

    files = (
        query.order_by(UploadedFile.review_priority.desc(), UploadedFile.created_at.asc())
        .limit(max(1, min(limit, 200)))
        .all()
    )

    summaries = [build_file_summary(file_record) for file_record in files]
    return {
        "count": len(summaries),
        "files": summaries,
    }


@router.get("/review-queue/next", response_model=UploadedFileDetail)
async def get_next_review_item(
    rubric_id: int | None = None,
    exam_name: str | None = None,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    query = db.query(UploadedFile).filter(UploadedFile.review_status == "pending")
    if rubric_id is not None:
        query = query.filter(UploadedFile.rubric_id == rubric_id)
    if exam_name:
        query = query.filter(UploadedFile.exam_name == exam_name)

    file_record = (
        query.order_by(UploadedFile.review_priority.desc(), UploadedFile.created_at.asc())
        .first()
    )
    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No review items available",
        )

    return build_file_detail(file_record)


@router.get("/plagiarism/flags", response_model=PlagiarismFlagResponse)
async def get_plagiarism_flags(
    threshold: float = PLAGIARISM_THRESHOLD,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    files = (
        db.query(UploadedFile)
        .filter(UploadedFile.plagiarism_score >= threshold)
        .order_by(UploadedFile.plagiarism_score.desc(), UploadedFile.review_priority.desc())
        .all()
    )

    summaries = [build_file_summary(file_record) for file_record in files]
    return {
        "count": len(summaries),
        "files": summaries,
    }


@router.patch("/files/{file_id}/review", response_model=ReviewResponse)
async def review_file(
    file_id: int,
    payload: FileReviewRequest,
    current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    file_record = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded file not found",
        )

    if payload.review_status.value == "overridden" and payload.override_grading_result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="override_grading_result is required when review_status is overridden",
        )

    file_record.review_status = payload.review_status.value
    file_record.review_notes = payload.review_notes
    file_record.reviewed_by = current_user.email
    file_record.status = "reviewed"

    if payload.override_grading_result is not None:
        file_record.grading_result = serialize_grading_result(
            payload.override_grading_result
        )
        file_record.review_status = "overridden"

    update_ai_confidence(file_record)

    db.commit()
    db.refresh(file_record)

    return {
        "message": "Review saved successfully",
        "file": build_file_detail(file_record),
    }


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    total_files = db.query(UploadedFile).count()
    reviewed_files = db.query(UploadedFile).filter(UploadedFile.status == "reviewed").count()
    total_graded_files = (
        db.query(UploadedFile)
        .filter(
            or_(
                UploadedFile.status == "graded",
                UploadedFile.status == "reviewed",
            )
        )
        .count()
    )
    pending_review_files = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.review_status == "pending",
            UploadedFile.status == "graded",
        )
        .count()
    )
    failed_files = (
        db.query(UploadedFile)
        .filter(
            or_(
                UploadedFile.status == "ocr_failed",
                UploadedFile.status == "grading_failed",
            )
        )
        .count()
    )
    plagiarism_flagged_files = (
        db.query(UploadedFile)
        .filter(UploadedFile.plagiarism_score >= PLAGIARISM_THRESHOLD)
        .count()
    )
    rubric_count = db.query(GradingRubric).count()

    return {
        "total_uploaded_files": total_files,
        "total_graded_files": total_graded_files,
        "pending_review_files": pending_review_files,
        "failed_files": failed_files,
        "reviewed_files": reviewed_files,
        "plagiarism_flagged_files": plagiarism_flagged_files,
        "rubric_count": rubric_count,
    }
