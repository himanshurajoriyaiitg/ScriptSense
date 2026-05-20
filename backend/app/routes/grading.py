from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth import require_roles
from app.models.file_model import UploadedFile
from app.models.user_model import User
from app.schemas.api import (
    GradeRequest,
    GradeResponse,
    RegradeFileRequest,
    UploadedFileDetail,
    UserRole,
)
from app.services.grading_service import grade_answer
from app.services.pdf_service import (
    FileValidationError,
    build_file_detail,
    regrade_submission,
)

router = APIRouter(tags=["grading"])


@router.post("/grade", response_model=GradeResponse)
async def grade(
    payload: GradeRequest,
    _current_user: User = Depends(
        require_roles(UserRole.instructor.value, UserRole.ta.value)
    ),
):
    result = grade_answer(payload.answer, payload.rubric)

    return {
        "grading_result": result
    }


@router.post("/grade/file/{file_id}", response_model=UploadedFileDetail)
async def regrade_uploaded_file(
    file_id: int,
    payload: RegradeFileRequest,
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

    if not file_record.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This file does not have OCR text available for grading",
        )

    try:
        file_record = regrade_submission(
            db=db,
            file_record=file_record,
            rubric_id=payload.rubric_id,
            rubric_payload=payload.rubric,
        )
    except FileValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return build_file_detail(file_record)
