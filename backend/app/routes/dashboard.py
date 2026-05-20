from fastapi import APIRouter
from app.database.db import SessionLocal
from app.models.file_model import UploadedFile

router = APIRouter()

@router.get("/files")
async def get_all_files():

    db = SessionLocal()

    files = db.query(UploadedFile).all()

    result = []

    for file in files:

        result.append({
            "id": file.id,
            "filename": file.filename,
            "grading_result": file.grading_result
        })

    db.close()

    return result

@router.get("/stats")
async def get_stats():

    db = SessionLocal()

    total_files = db.query(UploadedFile).count()

    db.close()

    return {
        "total_uploaded_files": total_files
    }