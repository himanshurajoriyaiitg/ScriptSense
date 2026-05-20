from contextlib import asynccontextmanager
import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import APP_NAME, APP_VERSION, ARTIFACT_DIR, CORS_ORIGINS, ENVIRONMENT, UPLOAD_DIR
from app.core.logging import configure_logging, get_logger, request_id_context
from app.database.db import init_db
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.grading import router as grading_router
from app.routes.jobs import router as jobs_router
from app.routes.rubrics import router as rubric_router
from app.routes.upload import router as upload_router
import os

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(grading_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(rubric_router)
app.include_router(jobs_router)


@app.middleware("http")
async def request_context_middleware(request, call_next):
    request_id = request.headers.get("X-Request-ID", uuid4().hex[:12])
    token = request_id_context.set(request_id)
    started_at = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled exception for %s %s", request.method, request.url.path)
        response = JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
            },
        )
    finally:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info(
            "%s %s completed in %sms",
            request.method,
            request.url.path,
            duration_ms,
        )
        request_id_context.reset(token)

    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/")
def home():
    return {
        "message": "ScriptSense Backend Running",
        "service": "GradeOps / ScriptSense API",
        "version": APP_VERSION,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "scriptsense-backend",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
    }
