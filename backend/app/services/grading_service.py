import json
from typing import Any

from openai import OpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
from app.services.rubric_service import format_rubric_for_prompt, normalize_rubric_definition

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class GradingServiceError(Exception):
    pass


def _extract_keywords(criterion: dict[str, Any]) -> set[str]:
    keywords: set[str] = set()

    for field in ("expected_points", "strict_keywords"):
        for item in criterion.get(field, []) or []:
            for token in str(item).lower().replace("/", " ").replace(",", " ").split():
                cleaned = "".join(char for char in token if char.isalnum())
                if len(cleaned) > 2:
                    keywords.add(cleaned)

    return keywords


def _build_fallback_grade(answer_text: str, rubric: dict[str, Any] | str) -> dict[str, Any]:
    normalized_rubric = normalize_rubric_definition(rubric)
    if normalized_rubric is None:
        return {
            "status": "pending_ai_configuration",
            "score_breakdown": [],
            "total_marks": None,
            "feedback": "AI grading is unavailable and the rubric is not structured JSON.",
            "missing_points": [],
            "summary": "Submission is ready for manual review.",
            "confidence": 0.2,
        }

    answer_lower = answer_text.lower()
    total_awarded = 0.0
    total_available = 0.0
    score_breakdown: list[dict[str, Any]] = []
    missing_points: list[str] = []
    confidence_values: list[float] = []

    for criterion in normalized_rubric.get("criteria", []):
        max_marks = float(criterion.get("max_marks", 0) or 0)
        total_available += max_marks
        keywords = _extract_keywords(criterion)
        if keywords:
            matched_keywords = [keyword for keyword in keywords if keyword in answer_lower]
            coverage = len(matched_keywords) / len(keywords)
        else:
            matched_keywords = []
            coverage = 0.5 if answer_lower else 0.0

        awarded_marks = round(max_marks * coverage, 2)
        total_awarded += awarded_marks
        confidence_values.append(coverage)

        expected_points = criterion.get("expected_points", []) or []
        missing = [
            point for point in expected_points if point.lower() not in answer_lower
        ]
        missing_points.extend(missing)

        score_breakdown.append(
            {
                "criterion": criterion.get("title", "Criterion"),
                "awarded_marks": awarded_marks,
                "max_marks": max_marks,
                "reason": (
                    f"Matched {len(matched_keywords)} of {len(keywords)} rubric keywords."
                    if keywords
                    else "No structured keywords available, so this criterion needs manual review."
                ),
            }
        )

    confidence = round(
        sum(confidence_values) / len(confidence_values), 4
    ) if confidence_values else 0.25

    return {
        "status": "heuristic_review_required",
        "score_breakdown": score_breakdown,
        "total_marks": round(total_awarded, 2),
        "feedback": (
            "Generated with the built-in fallback grader because OpenAI is not configured."
        ),
        "missing_points": missing_points[:10],
        "summary": "Heuristic grading completed. Manual review is still recommended.",
        "confidence": confidence,
    }


def grade_answer(answer_text: str, rubric: dict[str, Any] | str) -> dict[str, Any]:
    cleaned_answer = answer_text.strip()

    if not cleaned_answer:
        raise GradingServiceError("Cannot grade an empty answer")

    rubric_prompt = format_rubric_for_prompt(rubric)
    if not rubric_prompt:
        raise GradingServiceError("A rubric is required for grading")

    if client is None:
        return _build_fallback_grade(cleaned_answer, rubric)

    prompt = f"""
You are an expert exam evaluator working inside a human-in-the-loop grading system.

Grade the student answer strictly against the rubric and return valid JSON with this exact shape:
{{
  "status": "graded",
  "score_breakdown": [
    {{
      "criterion": "string",
      "awarded_marks": "number",
      "max_marks": "number",
      "reason": "string"
    }}
  ],
  "total_marks": "number",
  "feedback": "string",
  "missing_points": ["string"],
  "summary": "string",
  "confidence": "number between 0 and 1"
}}

Rubric:
{rubric_prompt}

Student Answer:
{cleaned_answer}
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict but fair examiner. "
                        "Only return valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
    except Exception as exc:
        raise GradingServiceError(f"Grading request failed: {exc}") from exc

    content = response.choices[0].message.content or "{}"

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "status": "graded",
            "score_breakdown": [],
            "total_marks": None,
            "feedback": "Model returned a non-JSON response.",
            "missing_points": [],
            "summary": "The grading response could not be fully structured.",
            "confidence": 0.35,
            "raw_response": content,
        }

    parsed.setdefault("status", "graded")
    parsed.setdefault("score_breakdown", [])
    parsed.setdefault("total_marks", None)
    parsed.setdefault("feedback", "")
    parsed.setdefault("missing_points", [])
    parsed.setdefault("summary", "")
    parsed.setdefault("confidence", 0.5)

    return parsed
