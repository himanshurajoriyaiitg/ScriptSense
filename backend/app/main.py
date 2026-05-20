from fastapi import FastAPI
from app.routes.upload import router as upload_router

from app.database.db import engine
from app.models.file_model import UploadedFile
from app.database.db import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(upload_router)

@app.get("/")
def home():
    return {"message": "ScriptSense Backend Running"}