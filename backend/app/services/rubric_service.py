import json
from typing import Any

from app.models.rubric_model import GradingRubric


def serialize_json_payload(payload: Any) -> str | None:
    if payload is None:
        return None
    if isinstance(payload, str):
        return payload
    return json.dumps(payload)


def deserialize_json_payload(payload: str | None) -> Any:
    if not payload:
        return None

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return payload


def normalize_rubric_definition(rubric: Any) -> dict[str, Any] | None:
    if rubric is None:
        return None

    if isinstance(rubric, dict):
        return rubric

    if isinstance(rubric, str):
        try:
            parsed = json.loads(rubric)
        except json.JSONDecodeError:
            return None

        if isinstance(parsed, dict):
            return parsed

    return None


def format_rubric_for_prompt(rubric: Any) -> str:
    normalized = normalize_rubric_definition(rubric)
    if normalized is None:
        return str(rubric).strip()

    lines = [
        f"Rubric Title: {normalized.get('title', 'Untitled Rubric')}",
        f"Exam Name: {normalized.get('exam_name', 'Unknown Exam')}",
        f"Total Marks: {normalized.get('total_marks', 'Not specified')}",
    ]

    description = normalized.get("description")
    if description:
        lines.append(f"Description: {description}")

    instructions = normalized.get("instructions")
    if instructions:
        lines.append(f"Instructions: {instructions}")

    criteria = normalized.get("criteria", [])
    if criteria:
        lines.append("Criteria:")
        for index, criterion in enumerate(criteria, start=1):
            title = criterion.get("title", f"Criterion {index}")
            max_marks = criterion.get("max_marks", "N/A")
            lines.append(f"{index}. {title} ({max_marks} marks)")

            expected_points = criterion.get("expected_points") or []
            if expected_points:
                lines.append("Expected points:")
                lines.extend(f"- {point}" for point in expected_points)

            strict_keywords = criterion.get("strict_keywords") or []
            if strict_keywords:
                lines.append(f"Strict keywords: {', '.join(strict_keywords)}")

            partial_credit_rules = criterion.get("partial_credit_rules") or []
            if partial_credit_rules:
                lines.append("Partial credit rules:")
                lines.extend(f"- {rule}" for rule in partial_credit_rules)

            notes = criterion.get("notes")
            if notes:
                lines.append(f"Notes: {notes}")

    return "\n".join(lines).strip()


def build_rubric_summary(rubric: GradingRubric) -> dict[str, Any]:
    parsed = deserialize_json_payload(rubric.rubric_json) or {}
    criteria = parsed.get("criteria", []) if isinstance(parsed, dict) else []

    return {
        "id": rubric.id,
        "title": rubric.title,
        "exam_name": rubric.exam_name,
        "description": rubric.description,
        "instructions": rubric.instructions,
        "total_marks": rubric.total_marks,
        "criteria_count": len(criteria),
        "is_active": rubric.is_active,
        "created_by_id": rubric.created_by_id,
        "created_at": rubric.created_at,
        "updated_at": rubric.updated_at,
    }


def build_rubric_detail(rubric: GradingRubric) -> dict[str, Any]:
    detail = build_rubric_summary(rubric)
    parsed = deserialize_json_payload(rubric.rubric_json)
    detail["criteria"] = parsed.get("criteria", []) if isinstance(parsed, dict) else []
    return detail
