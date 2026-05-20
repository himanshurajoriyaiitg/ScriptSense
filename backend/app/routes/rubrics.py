from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth import require_roles
from app.models.file_model import UploadedFile
from app.models.rubric_model import GradingRubric
from app.models.user_model import User
from app.schemas.api import (
    RubricCreateRequest,
    RubricDetailResponse,
    RubricSummaryResponse,
    UploadedFileSummary,
    UserRole,
)
from app.services.pdf_service import build_file_summary
from app.services.rubric_service import (
    build_rubric_detail,
    build_rubric_summary,
    serialize_json_payload,
)

router = APIRouter(tags=["rubrics"])


@router.post(
    "/rubrics",
    response_model=RubricDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rubric(
    payload: RubricCreateRequest,
    current_user: User = Depends(require_roles(UserRole.instructor.value)),
    db: Session = Depends(get_db),
):
    rubric_definition = {
        "title": payload.title,
        "exam_name": payload.exam_name,
        "description": payload.description,
        "instructions": payload.instructions,
        "total_marks": payload.total_marks,
        "criteria": [criterion.model_dump() for criterion in payload.criteria],
    }

    rubric = GradingRubric(
        title=payload.title,
        exam_name=payload.exam_name,
        description=payload.description,
        instructions=payload.instructions,
        total_marks=payload.total_marks,
        rubric_json=serialize_json_payload(rubric_definition) or "{}",
        is_active=payload.is_active,
        created_by_id=current_user.id,
    )
    db.add(rubric)
    db.commit()
    db.refresh(rubric)

    return build_rubric_detail(rubric)


@router.get("/rubrics", response_model=list[RubricSummaryResponse])
async def list_rubrics(
    active_only: bool = True,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    query = db.query(GradingRubric).order_by(
        GradingRubric.updated_at.desc(),
        GradingRubric.id.desc(),
    )
    if active_only:
        query = query.filter(GradingRubric.is_active.is_(True))

    return [build_rubric_summary(rubric) for rubric in query.all()]


@router.get("/rubrics/{rubric_id}", response_model=RubricDetailResponse)
async def get_rubric(
    rubric_id: int,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    rubric = db.query(GradingRubric).filter(GradingRubric.id == rubric_id).first()
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rubric not found",
        )

    return build_rubric_detail(rubric)


@router.get("/rubrics/{rubric_id}/files", response_model=list[UploadedFileSummary])
async def list_rubric_files(
    rubric_id: int,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
    db: Session = Depends(get_db),
):
    rubric = db.query(GradingRubric).filter(GradingRubric.id == rubric_id).first()
    if rubric is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rubric not found",
        )

    files = (
        db.query(UploadedFile)
        .filter(UploadedFile.rubric_id == rubric_id)
        .order_by(UploadedFile.review_priority.desc(), UploadedFile.created_at.desc())
        .all()
    )
    return [build_file_summary(file_record) for file_record in files]
