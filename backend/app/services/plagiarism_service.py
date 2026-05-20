from difflib import SequenceMatcher
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import DEFAULT_REVIEW_PRIORITY, MAX_PLAGIARISM_MATCHES
from app.models.file_model import UploadedFile
from app.services.rubric_service import deserialize_json_payload, serialize_json_payload


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in "".join(char.lower() if char.isalnum() else " " for char in text).split()
        if len(token) > 2
    }


def compute_similarity_score(text_a: str, text_b: str) -> float:
    if not text_a.strip() or not text_b.strip():
        return 0.0

    sequence_ratio = SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()

    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)
    if not tokens_a or not tokens_b:
        jaccard_ratio = 0.0
    else:
        jaccard_ratio = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

    return round((sequence_ratio * 0.6) + (jaccard_ratio * 0.4), 4)


def calculate_review_priority(file_record: UploadedFile) -> int:
    priority = DEFAULT_REVIEW_PRIORITY

    if file_record.processing_error:
        priority += 30

    if file_record.status in {"ocr_failed", "grading_failed"}:
        priority += 25

    if file_record.review_status == "pending":
        priority += 10

    if file_record.ai_confidence is None:
        priority += 8
    else:
        priority += round((1 - max(0.0, min(file_record.ai_confidence, 1.0))) * 25)

    priority += round((file_record.plagiarism_score or 0.0) * 30)
    return max(1, min(100, priority))


def update_ai_confidence(file_record: UploadedFile) -> None:
    parsed_result = deserialize_json_payload(file_record.grading_result)

    confidence: float | None = None
    if isinstance(parsed_result, dict):
        raw_confidence = parsed_result.get("confidence")
        try:
            if raw_confidence is not None:
                confidence = max(0.0, min(float(raw_confidence), 1.0))
        except (TypeError, ValueError):
            confidence = None

    file_record.ai_confidence = confidence
    file_record.review_priority = calculate_review_priority(file_record)


def _peer_query(db: Session, file_record: UploadedFile):
    peer_query = db.query(UploadedFile).filter(UploadedFile.id != file_record.id)
    if file_record.rubric_id is not None:
        peer_query = peer_query.filter(UploadedFile.rubric_id == file_record.rubric_id)
    elif file_record.exam_name:
        peer_query = peer_query.filter(UploadedFile.exam_name == file_record.exam_name)
    elif file_record.cohort_name:
        peer_query = peer_query.filter(UploadedFile.cohort_name == file_record.cohort_name)

    return peer_query


def _apply_plagiarism_metrics(db: Session, file_record: UploadedFile) -> None:
    if not file_record.extracted_text:
        file_record.plagiarism_score = 0.0
        file_record.plagiarism_matches = None
        file_record.review_priority = calculate_review_priority(file_record)
        return

    peers = _peer_query(db, file_record).all()
    matches: list[dict[str, Any]] = []

    for peer in peers:
        if not peer.extracted_text:
            continue

        score = compute_similarity_score(file_record.extracted_text, peer.extracted_text)
        if score <= 0:
            continue

        matches.append(
            {
                "file_id": peer.id,
                "filename": peer.filename,
                "student_identifier": peer.student_identifier,
                "score": score,
            }
        )

    matches.sort(key=lambda match: match["score"], reverse=True)
    top_matches = matches[:MAX_PLAGIARISM_MATCHES]
    file_record.plagiarism_score = top_matches[0]["score"] if top_matches else 0.0
    file_record.plagiarism_matches = serialize_json_payload(top_matches)
    file_record.review_priority = calculate_review_priority(file_record)


def refresh_plagiarism_signals(db: Session, file_record: UploadedFile) -> None:
    impacted_peers = _peer_query(db, file_record).all()
    _apply_plagiarism_metrics(db, file_record)

    for peer in impacted_peers:
        _apply_plagiarism_metrics(db, peer)
