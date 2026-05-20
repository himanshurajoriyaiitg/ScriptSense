from pathlib import Path

from app.core.config import ARTIFACT_DIR


def ensure_storage_dirs() -> None:
    Path(ARTIFACT_DIR).mkdir(parents=True, exist_ok=True)


def store_bytes(
    namespace: str,
    filename: str,
    payload: bytes,
) -> dict[str, str]:
    ensure_storage_dirs()

    namespace_path = Path(ARTIFACT_DIR) / namespace
    namespace_path.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(filename).name
    target_path = namespace_path / safe_filename
    target_path.write_bytes(payload)

    storage_key = str(target_path.relative_to(Path(ARTIFACT_DIR)))

    return {
        "storage_key": storage_key,
        "local_path": str(target_path.resolve()),
    }
