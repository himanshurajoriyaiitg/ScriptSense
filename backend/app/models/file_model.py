from sqlalchemy import Column, Integer, String, Text
from app.database.db import Base

class UploadedFile(Base):

    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    filepath = Column(String, nullable=False)

    extracted_text = Column(Text, nullable=True)