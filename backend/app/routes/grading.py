from fastapi import APIRouter
from app.services.grading_service import grade_answer

router = APIRouter()

@router.post("/grade")
async def grade(data: dict):

    answer_text = data.get("answer")

    result = grade_answer(answer_text)

    return {
        "grading_result": result
    }