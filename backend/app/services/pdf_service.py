import os
import uuid

from app.models.file_model import UploadedFile
from app.database.db import SessionLocal

from app.services.ocr_service import extract_text_from_pdf
from app.services.grading_service import grade_answer

UPLOAD_DIR = "uploads"

async def save_uploaded_file(file):

    if not file.filename.endswith(".pdf"):
        return None

    unique_id = str(uuid.uuid4())

    unique_filename = f"{unique_id}-{file.filename}"

    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    extracted_text = extract_text_from_pdf(file_path)

    grading_result = grade_answer(extracted_text)

    db = SessionLocal()

    new_file = UploadedFile(
        filename=file.filename,
        filepath=file_path,
        extracted_text=extracted_text,
        grading_result=grading_result
    )

    db.add(new_file)

    db.commit()

    db.refresh(new_file)

    db.close()

    return {
        "id": new_file.id,
        "grading_result": grading_result
    }