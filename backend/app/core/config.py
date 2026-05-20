import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "ScriptSense Backend")
APP_VERSION = os.getenv("APP_VERSION", "0.3.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scriptsense.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "10"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ARTIFACT_DIR = os.getenv("ARTIFACT_DIR", "artifacts")
MAX_UPLOAD_FILE_SIZE = int(os.getenv("MAX_UPLOAD_FILE_SIZE", str(25 * 1024 * 1024)))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
PLAGIARISM_THRESHOLD = float(os.getenv("PLAGIARISM_THRESHOLD", "0.72"))
MAX_PLAGIARISM_MATCHES = int(os.getenv("MAX_PLAGIARISM_MATCHES", "5"))
DEFAULT_REVIEW_PRIORITY = int(os.getenv("DEFAULT_REVIEW_PRIORITY", "55"))
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "gradeops-hitl-v1")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
