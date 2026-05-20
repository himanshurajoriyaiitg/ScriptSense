import fitz
from sqlalchemy.orm import Session

from app.models.artifact_model import SubmissionArtifact
from app.models.file_model import UploadedFile
from app.services.rubric_service import deserialize_json_payload, serialize_json_payload
from app.services.storage_service import store_bytes


def build_artifact_summary(artifact: SubmissionArtifact) -> dict:
    return {
        "id": artifact.id,
        "file_id": artifact.file_id,
        "artifact_type": artifact.artifact_type,
        "page_number": artifact.page_number,
        "storage_key": artifact.storage_key,
        "content_type": artifact.content_type,
        "width": artifact.width,
        "height": artifact.height,
        "url": f"/artifacts/{artifact.id}",
        "created_at": artifact.created_at.isoformat() if artifact.created_at else None,
    }


def generate_page_artifacts(
    db: Session,
    file_record: UploadedFile,
) -> list[dict]:
    db.query(SubmissionArtifact).filter(SubmissionArtifact.file_id == file_record.id).delete()
    db.flush()

    artifacts: list[SubmissionArtifact] = []

    with fitz.open(file_record.filepath) as doc:
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            pix = page.get_pixmap(dpi=170)
            stored = store_bytes(
                namespace=f"submissions/{file_record.id}/pages",
                filename=f"page-{page_number + 1}.png",
                payload=pix.tobytes("png"),
            )
            artifact = SubmissionArtifact(
                file_id=file_record.id,
                artifact_type="page_image",
                page_number=page_number + 1,
                storage_key=stored["storage_key"],
                local_path=stored["local_path"],
                content_type="image/png",
                width=pix.width,
                height=pix.height,
            )
            db.add(artifact)
            artifacts.append(artifact)

    db.flush()
    summaries = [build_artifact_summary(artifact) for artifact in artifacts]
    file_record.artifact_manifest = serialize_json_payload(summaries)
    return summaries


def get_file_artifact_summaries(file_record: UploadedFile) -> list[dict]:
    stored_manifest = deserialize_json_payload(file_record.artifact_manifest)
    if isinstance(stored_manifest, list):
        return stored_manifest
    return []
