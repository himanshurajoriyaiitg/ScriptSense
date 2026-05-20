import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.dependencies.auth import require_roles
from app.models.user_model import User
from app.schemas.api import (
    BulkUploadResponse,
    SingleUploadResponse,
    UploadManifestEntry,
    UploadedFileSummary,
    UserRole,
)
from app.services.job_service import (
    build_job_summary,
    create_processing_job,
    finalize_processing_job,
    update_processing_job_counts,
)
from app.services.pdf_service import (
    FileValidationError,
    build_file_detail,
    build_file_summary,
    save_uploaded_file,
)

router = APIRouter(tags=["upload"])


def _parse_rubric_payload(
    rubric_json: str | None,
    rubric_text: str | None,
):
    if rubric_json:
        try:
            return json.loads(rubric_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="rubric_json must be valid JSON",
            ) from exc

    if rubric_text and rubric_text.strip():
        return rubric_text.strip()

    return None


def _parse_manifest(manifest_json: str | None) -> dict[str, UploadManifestEntry]:
    if not manifest_json:
        return {}

    try:
        parsed = json.loads(manifest_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="manifest_json must be valid JSON",
        ) from exc

    if isinstance(parsed, dict):
        if "entries" in parsed and isinstance(parsed["entries"], list):
            entries = parsed["entries"]
        else:
            entries = [
                {"filename": filename, **(metadata or {})}
                for filename, metadata in parsed.items()
            ]
    elif isinstance(parsed, list):
        entries = parsed
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="manifest_json must be a list or an object keyed by filename",
        )

    manifest: dict[str, UploadManifestEntry] = {}
    for entry in entries:
        validated = UploadManifestEntry.model_validate(entry)
        manifest[validated.filename] = validated

    return manifest


@router.post("/upload", response_model=SingleUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    rubric_id: int | None = Form(default=None),
    rubric_json: str | None = Form(default=None),
    rubric_text: str | None = Form(default=None),
    student_identifier: str | None = Form(default=None),
    exam_name: str | None = Form(default=None),
    cohort_name: str | None = Form(default=None),
    auto_grade: bool = Form(default=True),
    current_user: User = Depends(require_roles(UserRole.instructor.value)),
    db: Session = Depends(get_db),
):
    rubric_payload = _parse_rubric_payload(rubric_json, rubric_text)
    job = create_processing_job(
        db,
        requested_by_id=current_user.id,
        job_type="single_upload",
        total_files=1,
        rubric_id=rubric_id,
        message="Single PDF submission processing",
    )

    try:
        saved_file = await save_uploaded_file(
            file=file,
            db=db,
            uploader_id=current_user.id,
            processing_job=job,
            rubric_id=rubric_id,
            rubric_payload=rubric_payload,
            student_identifier=student_identifier,
            exam_name=exam_name,
            cohort_name=cohort_name,
            auto_grade=auto_grade,
        )
    except FileValidationError as exc:
        update_processing_job_counts(db, job, failed_increment=1)
        finalize_processing_job(
            db,
            job,
            summary={"error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if saved_file.status in {"ocr_failed", "grading_failed"}:
        update_processing_job_counts(db, job, failed_increment=1)
    else:
        update_processing_job_counts(db, job, processed_increment=1)
    finalize_processing_job(
        db,
        job,
        summary={"file_ids": [saved_file.id], "status": saved_file.status},
    )

    return {
        "message": "PDF uploaded successfully",
        "file_id": saved_file.id,
        "job": build_job_summary(job),
        "file": build_file_detail(saved_file),
    }


@router.post("/upload/bulk", response_model=BulkUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_bulk_pdfs(
    files: list[UploadFile] = File(...),
    rubric_id: int | None = Form(default=None),
    rubric_json: str | None = Form(default=None),
    rubric_text: str | None = Form(default=None),
    exam_name: str | None = Form(default=None),
    cohort_name: str | None = Form(default=None),
    manifest_json: str | None = Form(default=None),
    auto_grade: bool = Form(default=True),
    current_user: User = Depends(require_roles(UserRole.instructor.value)),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one PDF file is required",
        )

    rubric_payload = _parse_rubric_payload(rubric_json, rubric_text)
    manifest = _parse_manifest(manifest_json)
    job = create_processing_job(
        db,
        requested_by_id=current_user.id,
        job_type="bulk_upload",
        total_files=len(files),
        rubric_id=rubric_id,
        message="Bulk PDF submission processing",
    )
    processed_files: list[UploadedFileSummary] = []
    failed_filenames: list[str] = []

    for file in files:
        manifest_entry = manifest.get(file.filename or "")
        entry_rubric_id = (
            manifest_entry.rubric_id
            if manifest_entry and manifest_entry.rubric_id is not None
            else rubric_id
        )
        entry_exam_name = (
            manifest_entry.exam_name if manifest_entry and manifest_entry.exam_name else exam_name
        )
        entry_cohort_name = (
            manifest_entry.cohort_name
            if manifest_entry and manifest_entry.cohort_name
            else cohort_name
        )
        entry_student_identifier = (
            manifest_entry.student_identifier if manifest_entry else None
        )
        entry_auto_grade = (
            manifest_entry.auto_grade
            if manifest_entry and manifest_entry.auto_grade is not None
            else auto_grade
        )

        try:
            saved_file = await save_uploaded_file(
                file=file,
                db=db,
                uploader_id=current_user.id,
                processing_job=job,
                rubric_id=entry_rubric_id,
                rubric_payload=rubric_payload,
                student_identifier=entry_student_identifier,
                exam_name=entry_exam_name,
                cohort_name=entry_cohort_name,
                auto_grade=entry_auto_grade,
            )
            processed_files.append(UploadedFileSummary(**build_file_summary(saved_file)))
            if saved_file.status in {"ocr_failed", "grading_failed"}:
                update_processing_job_counts(db, job, failed_increment=1)
                failed_filenames.append(saved_file.filename)
            else:
                update_processing_job_counts(db, job, processed_increment=1)
        except FileValidationError as exc:
            update_processing_job_counts(db, job, failed_increment=1)
            failed_filenames.append(file.filename or "unknown.pdf")
            finalize_processing_job(
                db,
                job,
                summary={
                    "failed_filenames": failed_filenames,
                    "processed_file_ids": [file_summary.id for file_summary in processed_files],
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{file.filename}: {exc}",
            ) from exc

    finalize_processing_job(
        db,
        job,
        summary={
            "processed_file_ids": [file_summary.id for file_summary in processed_files],
            "failed_filenames": failed_filenames,
        },
    )

    return {
        "message": f"{len(processed_files)} PDF files processed successfully",
        "processed_count": len(processed_files),
        "job": build_job_summary(job),
        "files": processed_files,
    }
