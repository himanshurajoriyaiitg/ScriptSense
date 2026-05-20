from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class UserRole(str, Enum):
    instructor = "instructor"
    ta = "ta"


class FileStatus(str, Enum):
    uploaded = "uploaded"
    ocr_completed = "ocr_completed"
    needs_rubric = "needs_rubric"
    graded = "graded"
    ocr_failed = "ocr_failed"
    grading_failed = "grading_failed"
    reviewed = "reviewed"


class ReviewStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    overridden = "overridden"
    rejected = "rejected"


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    completed_with_errors = "completed_with_errors"
    failed = "failed"


def _normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("A valid email address is required")
    return email


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned or None


class SignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.instructor

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _normalize_email(value)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Password is required")
        return cleaned


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: UserRole
    created_at: datetime | None = None


class SignupResponse(BaseModel):
    message: str
    user: UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RubricCriterion(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    max_marks: float = Field(gt=0)
    expected_points: list[str] = Field(default_factory=list)
    strict_keywords: list[str] = Field(default_factory=list)
    partial_credit_rules: list[str] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("title", "description", "notes")
    @classmethod
    def strip_optional_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("expected_points", "strict_keywords", "partial_credit_rules")
    @classmethod
    def strip_list_values(cls, values: list[str]) -> list[str]:
        cleaned = [item.strip() for item in values if item.strip()]
        return cleaned


class RubricCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    exam_name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    instructions: str | None = None
    total_marks: str = Field(min_length=1, max_length=32)
    criteria: list[RubricCriterion] = Field(min_length=1)
    is_active: bool = True

    @field_validator("title", "exam_name", "description", "instructions", "total_marks")
    @classmethod
    def strip_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("This field cannot be empty")
        return cleaned


class RubricSummaryResponse(BaseModel):
    id: int
    title: str
    exam_name: str
    description: str | None = None
    instructions: str | None = None
    total_marks: str
    criteria_count: int
    is_active: bool
    created_by_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RubricDetailResponse(RubricSummaryResponse):
    criteria: list[RubricCriterion]


class GradeRequest(BaseModel):
    answer: str = Field(min_length=1)
    rubric: dict[str, Any] | str

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Answer cannot be empty")
        return cleaned

    @field_validator("rubric")
    @classmethod
    def validate_rubric(cls, value: dict[str, Any] | str) -> dict[str, Any] | str:
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                raise ValueError("Rubric cannot be empty")
            return cleaned

        if not value:
            raise ValueError("Rubric cannot be empty")
        return value


class RegradeFileRequest(BaseModel):
    rubric_id: int | None = None
    rubric: dict[str, Any] | str | None = None

    @model_validator(mode="after")
    def validate_rubric_source(self):
        if self.rubric_id is None and self.rubric is None:
            raise ValueError("Either rubric_id or rubric must be provided")
        return self


class GradeResponse(BaseModel):
    grading_result: Any


class UploadManifestEntry(BaseModel):
    filename: str = Field(min_length=1)
    student_identifier: str | None = None
    exam_name: str | None = None
    cohort_name: str | None = None
    rubric_id: int | None = None
    auto_grade: bool | None = None

    @field_validator("filename", "student_identifier", "exam_name", "cohort_name")
    @classmethod
    def strip_manifest_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Manifest values cannot be empty strings")
        return cleaned


class PlagiarismMatch(BaseModel):
    file_id: int
    filename: str
    student_identifier: str | None = None
    score: float


class PipelineEvent(BaseModel):
    stage: str
    status: str
    message: str
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactSummaryResponse(BaseModel):
    id: int
    file_id: int
    artifact_type: str
    page_number: int | None = None
    storage_key: str
    content_type: str
    width: int | None = None
    height: int | None = None
    url: str
    created_at: datetime | None = None


class UploadedFileSummary(BaseModel):
    id: int
    filename: str
    status: str
    review_status: str
    processing_job_id: int | None = None
    rubric_id: int | None = None
    rubric: Any | None = None
    grading_result: Any | None = None
    review_notes: str | None = None
    processing_error: str | None = None
    uploader_id: int | None = None
    reviewed_by: str | None = None
    student_identifier: str | None = None
    exam_name: str | None = None
    cohort_name: str | None = None
    page_count: int = 0
    ai_confidence: float | None = None
    plagiarism_score: float = 0
    plagiarism_matches: list[PlagiarismMatch] = Field(default_factory=list)
    artifacts: list[ArtifactSummaryResponse] = Field(default_factory=list)
    pipeline_trace: list[PipelineEvent] = Field(default_factory=list)
    review_priority: int = 0
    extracted_text_preview: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UploadedFileDetail(UploadedFileSummary):
    extracted_text: str | None = None


class ReviewQueueResponse(BaseModel):
    count: int
    files: list[UploadedFileSummary]


class ProcessingJobResponse(BaseModel):
    id: int
    job_type: str
    status: JobStatus | str
    pipeline_name: str
    requested_by_id: int | None = None
    rubric_id: int | None = None
    total_files: int
    processed_files: int
    failed_files: int
    message: str | None = None
    result_summary: Any | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SingleUploadResponse(BaseModel):
    message: str
    file_id: int
    job: ProcessingJobResponse
    file: UploadedFileDetail


class BulkUploadResponse(BaseModel):
    message: str
    processed_count: int
    job: ProcessingJobResponse
    files: list[UploadedFileSummary]


class FileReviewRequest(BaseModel):
    review_status: ReviewStatus
    review_notes: str | None = Field(default=None, max_length=2000)
    override_grading_result: dict[str, Any] | None = None

    @field_validator("review_notes")
    @classmethod
    def strip_optional_notes(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ReviewResponse(BaseModel):
    message: str
    file: UploadedFileDetail


class PlagiarismFlagResponse(BaseModel):
    count: int
    files: list[UploadedFileSummary]


class ArtifactListResponse(BaseModel):
    file_id: int
    count: int
    artifacts: list[ArtifactSummaryResponse]


class StatsResponse(BaseModel):
    total_uploaded_files: int
    total_graded_files: int
    pending_review_files: int
    failed_files: int
    reviewed_files: int
    plagiarism_flagged_files: int
    rubric_count: int


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class PipelineTraceResponse(BaseModel):
    file_id: int
    pipeline_trace: list[PipelineEvent]


class TokenPayload(BaseModel):
    sub: str
    role: str
    user_id: int | None = None
