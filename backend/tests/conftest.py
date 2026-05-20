import os
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB_PATH = Path("/tmp/scriptsense_pytest.db")
TEST_UPLOAD_DIR = Path("/tmp/scriptsense_pytest_uploads")
TEST_ARTIFACT_DIR = Path("/tmp/scriptsense_pytest_artifacts")

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ALGORITHM"] = "HS256"
os.environ["OPENAI_API_KEY"] = ""
os.environ["UPLOAD_DIR"] = str(TEST_UPLOAD_DIR)
os.environ["ARTIFACT_DIR"] = str(TEST_ARTIFACT_DIR)
os.environ["PLAGIARISM_THRESHOLD"] = "0.6"

import app.models.file_model  # noqa: E402,F401
import app.models.rubric_model  # noqa: E402,F401
import app.models.user_model  # noqa: E402,F401
from app.database.db import Base, engine, init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database():
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    shutil.rmtree(TEST_UPLOAD_DIR, ignore_errors=True)
    shutil.rmtree(TEST_ARTIFACT_DIR, ignore_errors=True)
    TEST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TEST_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    init_db()
    yield
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    shutil.rmtree(TEST_UPLOAD_DIR, ignore_errors=True)
    shutil.rmtree(TEST_ARTIFACT_DIR, ignore_errors=True)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def instructor_headers(client: TestClient):
    client.post(
        "/signup",
        json={
            "email": "instructor@example.com",
            "password": "password123",
            "role": "instructor",
        },
    )
    response = client.post(
        "/login",
        json={
            "email": "instructor@example.com",
            "password": "password123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def ta_headers(client: TestClient):
    client.post(
        "/signup",
        json={
            "email": "ta@example.com",
            "password": "password123",
            "role": "ta",
        },
    )
    response = client.post(
        "/login",
        json={
            "email": "ta@example.com",
            "password": "password123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_pdf_bytes():
    sample_pdf_path = Path(__file__).resolve().parents[1] / "uploads" / "aadharr.pdf"
    return sample_pdf_path.read_bytes()
