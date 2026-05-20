from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(20), nullable=False, default="instructor", server_default="instructor")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    uploaded_files = relationship("UploadedFile", back_populates="uploader")
    created_rubrics = relationship("GradingRubric", back_populates="creator")
    processing_jobs = relationship("ProcessingJob", back_populates="requested_by")
