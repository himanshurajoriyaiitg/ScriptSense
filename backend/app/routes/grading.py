from fastapi import APIRouter
from app.services.grading_service import grade_answer

router = APIRouter()

@router.post("/grade")
async def grade(data: dict):

    answer_text = data.get("answer")

    rubric = data.get("rubric")

    result = grade_answer(
        answer_text,
        rubric
    )

    return {
        "grading_result": result
    }