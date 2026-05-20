from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(32), nullable=False, default="upload", server_default="upload")
    status = Column(String(32), nullable=False, default="queued", server_default="queued")
    pipeline_name = Column(
        String(64),
        nullable=False,
        default="gradeops-hitl-v1",
        server_default="gradeops-hitl-v1",
    )
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rubric_id = Column(Integer, ForeignKey("grading_rubrics.id"), nullable=True)
    total_files = Column(Integer, nullable=False, default=0, server_default="0")
    processed_files = Column(Integer, nullable=False, default=0, server_default="0")
    failed_files = Column(Integer, nullable=False, default=0, server_default="0")
    message = Column(Text, nullable=True)
    result_summary = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    requested_by = relationship("User", back_populates="processing_jobs")
    linked_rubric = relationship("GradingRubric", back_populates="processing_jobs")
    uploaded_files = relationship("UploadedFile", back_populates="processing_job")
