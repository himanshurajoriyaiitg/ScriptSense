from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import save_uploaded_file

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    result = await save_uploaded_file(file)

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    return {
        "file_id": result["id"],
        "message": "PDF uploaded successfully"
    }