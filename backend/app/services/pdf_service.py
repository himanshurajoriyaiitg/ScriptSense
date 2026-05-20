import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import MAX_UPLOAD_FILE_SIZE, UPLOAD_DIR
from app.models.file_model import UploadedFile
from app.models.job_model import ProcessingJob
from app.models.rubric_model import GradingRubric
from app.services.artifact_service import generate_page_artifacts, get_file_artifact_summaries
from app.services.grading_service import GradingServiceError, grade_answer
from app.services.ocr_service import OCRProcessingError, extract_submission_content
from app.services.plagiarism_service import (
    calculate_review_priority,
    refresh_plagiarism_signals,
    update_ai_confidence,
)
from app.services.rubric_service import (
    deserialize_json_payload,
    serialize_json_payload,
)


class FileValidationError(Exception):
    pass


def _normalize_filename(filename: str | None) -> str:
    sanitized_name = Path(filename or "uploaded.pdf").name
    return sanitized_name or "uploaded.pdf"


def serialize_grading_result(grading_result: Any) -> str | None:
    if grading_result is None:
        return None
    return json.dumps(grading_result)


def deserialize_grading_result(grading_result: str | None) -> Any:
    return deserialize_json_payload(grading_result)


def _deserialize_pipeline_trace(file_record: UploadedFile) -> list[dict[str, Any]]:
    stored = deserialize_json_payload(file_record.pipeline_trace)
    if isinstance(stored, list):
        return stored
    return []


def _append_pipeline_event(
    file_record: UploadedFile,
    *,
    stage: str,
    status: str,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    trace = _deserialize_pipeline_trace(file_record)
    trace.append(
        {
            "stage": stage,
            "status": status,
            "message": message,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }
    )
    file_record.pipeline_trace = serialize_json_payload(trace)


def _normalize_rubric_snapshot(
    db: Session,
    rubric_id: int | None = None,
    rubric_payload: dict[str, Any] | str | None = None,
) -> tuple[int | None, str | None, GradingRubric | None]:
    if rubric_id is not None:
        rubric_record = db.query(GradingRubric).filter(GradingRubric.id == rubric_id).first()
        if rubric_record is None or not rubric_record.is_active:
            raise FileValidationError("The selected rubric was not found or is inactive")
        return rubric_record.id, rubric_record.rubric_json, rubric_record

    if rubric_payload is None:
        return None, None, None

    if isinstance(rubric_payload, str):
        cleaned = rubric_payload.strip()
        if not cleaned:
            return None, None, None
        return None, cleaned, None

    return None, serialize_json_payload(rubric_payload), None


def build_file_summary(file_record: UploadedFile) -> dict[str, Any]:
    preview = None
    if file_record.extracted_text:
        preview = file_record.extracted_text[:280]
        if len(file_record.extracted_text) > 280:
            preview = f"{preview}..."

    plagiarism_matches = deserialize_json_payload(file_record.plagiarism_matches)
    if not isinstance(plagiarism_matches, list):
        plagiarism_matches = []

    return {
        "id": file_record.id,
        "filename": file_record.filename,
        "status": file_record.status,
        "review_status": file_record.review_status,
        "processing_job_id": file_record.processing_job_id,
        "rubric_id": file_record.rubric_id,
        "rubric": deserialize_json_payload(file_record.rubric),
        "grading_result": deserialize_grading_result(file_record.grading_result),
        "review_notes": file_record.review_notes,
        "processing_error": file_record.processing_error,
        "uploader_id": file_record.uploader_id,
        "reviewed_by": file_record.reviewed_by,
        "student_identifier": file_record.student_identifier,
        "exam_name": file_record.exam_name,
        "cohort_name": file_record.cohort_name,
        "page_count": file_record.page_count or 0,
        "ai_confidence": file_record.ai_confidence,
        "plagiarism_score": round(file_record.plagiarism_score or 0.0, 4),
        "plagiarism_matches": plagiarism_matches,
        "artifacts": get_file_artifact_summaries(file_record),
        "pipeline_trace": _deserialize_pipeline_trace(file_record),
        "review_priority": file_record.review_priority,
        "extracted_text_preview": preview,
        "created_at": file_record.created_at,
        "updated_at": file_record.updated_at,
    }


def build_file_detail(file_record: UploadedFile) -> dict[str, Any]:
    detail = build_file_summary(file_record)
    detail["extracted_text"] = file_record.extracted_text
    return detail


def _store_grading_result(file_record: UploadedFile, grading_result: dict[str, Any]) -> None:
    file_record.grading_result = serialize_grading_result(grading_result)
    update_ai_confidence(file_record)
    _append_pipeline_event(
        file_record,
        stage="grading",
        status="completed",
        message="Structured grading completed",
        metadata={
            "confidence": grading_result.get("confidence"),
            "total_marks": grading_result.get("total_marks"),
        },
    )


def regrade_submission(
    db: Session,
    file_record: UploadedFile,
    rubric_id: int | None = None,
    rubric_payload: dict[str, Any] | str | None = None,
) -> UploadedFile:
    resolved_rubric_id, rubric_snapshot, rubric_record = _normalize_rubric_snapshot(
        db=db,
        rubric_id=rubric_id,
        rubric_payload=rubric_payload,
    )

    if not file_record.extracted_text:
        raise FileValidationError("This file does not have OCR text available for grading")

    file_record.rubric_id = resolved_rubric_id
    file_record.rubric = rubric_snapshot
    if rubric_record and not file_record.exam_name:
        file_record.exam_name = rubric_record.exam_name

    file_record.grading_result = None
    file_record.processing_error = None
    file_record.review_status = "pending"
    file_record.review_notes = None
    file_record.reviewed_by = None
    _append_pipeline_event(
        file_record,
        stage="rubric",
        status="completed",
        message="Rubric linked for regrading",
        metadata={"rubric_id": resolved_rubric_id},
    )

    try:
        grading_result = grade_answer(
            file_record.extracted_text,
            deserialize_json_payload(rubric_snapshot) or rubric_snapshot,
        )
        _store_grading_result(file_record, grading_result)
        file_record.status = "graded"
        file_record.processing_error = None
    except GradingServiceError as exc:
        file_record.status = "grading_failed"
        file_record.ai_confidence = None
        file_record.processing_error = str(exc)
        _append_pipeline_event(
            file_record,
            stage="grading",
            status="failed",
            message=str(exc),
        )

    _append_pipeline_event(
        file_record,
        stage="plagiarism",
        status="running",
        message="Refreshing similarity signals",
    )
    refresh_plagiarism_signals(db, file_record)
    _append_pipeline_event(
        file_record,
        stage="plagiarism",
        status="completed",
        message="Similarity signals refreshed",
        metadata={"plagiarism_score": file_record.plagiarism_score},
    )
    db.commit()
    db.refresh(file_record)
    return file_record


async def save_uploaded_file(
    file,
    db: Session,
    uploader_id: int | None = None,
    processing_job: ProcessingJob | None = None,
    rubric_id: int | None = None,
    rubric_payload: dict[str, Any] | str | None = None,
    student_identifier: str | None = None,
    exam_name: str | None = None,
    cohort_name: str | None = None,
    auto_grade: bool = True,
) -> UploadedFile:
    safe_filename = _normalize_filename(file.filename)

    if not safe_filename.lower().endswith(".pdf"):
        raise FileValidationError("Only PDF files are allowed")

    content = await file.read()
    if not content:
        raise FileValidationError("Uploaded file is empty")

    if len(content) > MAX_UPLOAD_FILE_SIZE:
        raise FileValidationError(
            f"File exceeds the {MAX_UPLOAD_FILE_SIZE // (1024 * 1024)} MB upload limit"
        )

    resolved_rubric_id, rubric_snapshot, rubric_record = _normalize_rubric_snapshot(
        db=db,
        rubric_id=rubric_id,
        rubric_payload=rubric_payload,
    )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    unique_filename = f"{uuid.uuid4().hex}-{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    resolved_exam_name = (exam_name or "").strip() or None
    resolved_cohort_name = (cohort_name or "").strip() or None
    resolved_student_identifier = (student_identifier or "").strip() or None

    if rubric_record and not resolved_exam_name:
        resolved_exam_name = rubric_record.exam_name

    file_record = UploadedFile(
        filename=safe_filename,
        filepath=file_path,
        rubric_id=resolved_rubric_id,
        rubric=rubric_snapshot,
        processing_job_id=processing_job.id if processing_job else None,
        student_identifier=resolved_student_identifier,
        exam_name=resolved_exam_name,
        cohort_name=resolved_cohort_name,
        status="processing",
        review_status="pending",
        uploader_id=uploader_id,
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    _append_pipeline_event(
        file_record,
        stage="upload",
        status="completed",
        message="PDF stored successfully",
        metadata={
            "filename": safe_filename,
            "rubric_id": resolved_rubric_id,
            "processing_job_id": processing_job.id if processing_job else None,
        },
    )

    try:
        _append_pipeline_event(
            file_record,
            stage="ocr",
            status="running",
            message="Starting OCR extraction",
        )
        extraction_result = extract_submission_content(file_path)
        file_record.extracted_text = extraction_result["text"]
        file_record.page_count = extraction_result.get("page_count", 0)
        file_record.status = "ocr_completed"
        file_record.processing_error = None
        _append_pipeline_event(
            file_record,
            stage="ocr",
            status="completed",
            message="OCR extraction completed",
            metadata={"page_count": file_record.page_count},
        )
    except OCRProcessingError as exc:
        file_record.status = "ocr_failed"
        file_record.processing_error = str(exc)
        file_record.ai_confidence = None
        file_record.review_priority = calculate_review_priority(file_record)
        _append_pipeline_event(
            file_record,
            stage="ocr",
            status="failed",
            message=str(exc),
        )
        db.commit()
        db.refresh(file_record)
        return file_record

    try:
        _append_pipeline_event(
            file_record,
            stage="artifacts",
            status="running",
            message="Generating page review artifacts",
        )
        artifacts = generate_page_artifacts(db, file_record)
        _append_pipeline_event(
            file_record,
            stage="artifacts",
            status="completed",
            message="Page review artifacts generated",
            metadata={"artifact_count": len(artifacts)},
        )
    except Exception as exc:
        _append_pipeline_event(
            file_record,
            stage="artifacts",
            status="failed",
            message=f"Artifact generation failed: {exc}",
        )

    if rubric_snapshot and auto_grade:
        try:
            _append_pipeline_event(
                file_record,
                stage="rubric",
                status="completed",
                message="Rubric attached to submission",
                metadata={"rubric_id": resolved_rubric_id},
            )
            _append_pipeline_event(
                file_record,
                stage="grading",
                status="running",
                message="Starting structured grading",
            )
            grading_result = grade_answer(
                file_record.extracted_text,
                deserialize_json_payload(rubric_snapshot) or rubric_snapshot,
            )
            _store_grading_result(file_record, grading_result)
            file_record.status = "graded"
            file_record.processing_error = None
        except GradingServiceError as exc:
            file_record.status = "grading_failed"
            file_record.ai_confidence = None
            file_record.processing_error = str(exc)
            _append_pipeline_event(
                file_record,
                stage="grading",
                status="failed",
                message=str(exc),
            )
    elif rubric_snapshot:
        file_record.status = "ocr_completed"
        file_record.ai_confidence = None
        _append_pipeline_event(
            file_record,
            stage="rubric",
            status="completed",
            message="Rubric attached, waiting for manual or later grading",
            metadata={"rubric_id": resolved_rubric_id},
        )
    else:
        file_record.status = "needs_rubric"
        file_record.ai_confidence = None
        _append_pipeline_event(
            file_record,
            stage="rubric",
            status="pending",
            message="Submission needs a rubric before grading can start",
        )

    _append_pipeline_event(
        file_record,
        stage="plagiarism",
        status="running",
        message="Refreshing similarity signals",
    )
    refresh_plagiarism_signals(db, file_record)
    _append_pipeline_event(
        file_record,
        stage="plagiarism",
        status="completed",
        message="Similarity signals refreshed",
        metadata={"plagiarism_score": file_record.plagiarism_score},
    )
    db.commit()
    db.refresh(file_record)

    return file_record
