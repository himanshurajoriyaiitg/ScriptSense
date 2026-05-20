from fastapi import APIRouter, UploadFile, File
from app.services.pdf_service import save_uploaded_file

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    saved_path = await save_uploaded_file(file)

    return {
        "filename": file.filename,
        "saved_at": saved_path,
        "message": "File uploaded successfully"
    }