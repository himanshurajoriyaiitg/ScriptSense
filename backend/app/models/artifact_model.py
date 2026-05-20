from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class SubmissionArtifact(Base):
    __tablename__ = "submission_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False, index=True)
    artifact_type = Column(String(32), nullable=False, default="page_image", server_default="page_image")
    page_number = Column(Integer, nullable=True)
    storage_key = Column(String(512), nullable=False)
    local_path = Column(String(1024), nullable=False)
    content_type = Column(String(128), nullable=False, default="image/png", server_default="image/png")
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    uploaded_file = relationship("UploadedFile", back_populates="artifacts")
