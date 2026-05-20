from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)
    grading_result = Column(Text, nullable=True)
    rubric = Column(Text, nullable=True)
    rubric_id = Column(Integer, ForeignKey("grading_rubrics.id"), nullable=True)
    processing_job_id = Column(Integer, ForeignKey("processing_jobs.id"), nullable=True)
    student_identifier = Column(String(128), nullable=True)
    exam_name = Column(String(255), nullable=True)
    cohort_name = Column(String(255), nullable=True)
    page_count = Column(Integer, nullable=False, default=0, server_default="0")
    ai_confidence = Column(Float, nullable=True)
    plagiarism_score = Column(Float, nullable=False, default=0.0, server_default="0")
    plagiarism_matches = Column(Text, nullable=True)
    pipeline_trace = Column(Text, nullable=True)
    artifact_manifest = Column(Text, nullable=True)
    review_priority = Column(Integer, nullable=False, default=55, server_default="55")
    status = Column(String(32), nullable=False, default="uploaded", server_default="uploaded")
    review_status = Column(String(32), nullable=False, default="pending", server_default="pending")
    review_notes = Column(Text, nullable=True)
    processing_error = Column(Text, nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    uploader = relationship("User", back_populates="uploaded_files")
    linked_rubric = relationship("GradingRubric", back_populates="uploaded_files")
    processing_job = relationship("ProcessingJob", back_populates="uploaded_files")
    artifacts = relationship(
        "SubmissionArtifact",
        back_populates="uploaded_file",
        cascade="all, delete-orphan",
    )
