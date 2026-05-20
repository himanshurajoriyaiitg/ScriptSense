from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import relationship

from app.database.db import Base


class GradingRubric(Base):
    __tablename__ = "grading_rubrics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    exam_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    total_marks = Column(String(32), nullable=False)
    rubric_json = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    creator = relationship("User", back_populates="created_rubrics")
    uploaded_files = relationship("UploadedFile", back_populates="linked_rubric")
    processing_jobs = relationship("ProcessingJob", back_populates="linked_rubric")
