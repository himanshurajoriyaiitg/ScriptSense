from fastapi import APIRouter, UploadFile, File
import os

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {
        "filename": file.filename,
        "saved_at": file_path,
        "message": "File uploaded and saved successfully"
    }