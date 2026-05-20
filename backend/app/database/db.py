from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_column(table_name: str, column_name: str, definition: str) -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    if table_name not in existing_tables:
        return

    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in existing_columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")
        )


def run_startup_migrations() -> None:
    user_columns = {
        "role": "VARCHAR(20) NOT NULL DEFAULT 'instructor'",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }
    file_columns = {
        "rubric": "TEXT",
        "rubric_id": "INTEGER",
        "processing_job_id": "INTEGER",
        "student_identifier": "VARCHAR(128)",
        "exam_name": "VARCHAR(255)",
        "cohort_name": "VARCHAR(255)",
        "page_count": "INTEGER NOT NULL DEFAULT 0",
        "ai_confidence": "FLOAT",
        "plagiarism_score": "FLOAT NOT NULL DEFAULT 0",
        "plagiarism_matches": "TEXT",
        "pipeline_trace": "TEXT",
        "artifact_manifest": "TEXT",
        "review_priority": "INTEGER NOT NULL DEFAULT 55",
        "status": "VARCHAR(32) NOT NULL DEFAULT 'uploaded'",
        "review_status": "VARCHAR(32) NOT NULL DEFAULT 'pending'",
        "review_notes": "TEXT",
        "processing_error": "TEXT",
        "uploader_id": "INTEGER",
        "reviewed_by": "VARCHAR(255)",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }

    for column_name, definition in user_columns.items():
        _ensure_column("users", column_name, definition)

    for column_name, definition in file_columns.items():
        _ensure_column("uploaded_files", column_name, definition)


def init_db() -> None:
    import app.models.artifact_model  # noqa: F401
    import app.models.file_model  # noqa: F401
    import app.models.job_model  # noqa: F401
    import app.models.rubric_model  # noqa: F401
    import app.models.user_model  # noqa: F401

    Base.metadata.create_all(bind=engine)
    run_startup_migrations()
