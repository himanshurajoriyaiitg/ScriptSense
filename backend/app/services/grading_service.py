from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def grade_answer(answer_text, rubric):

    prompt = f"""
You are an expert exam evaluator.

Evaluate the student answer STRICTLY according to the rubric.

Rubric:
{rubric}

Student Answer:
{answer_text}

Give:
1. Marks breakdown
2. Total marks
3. Feedback
4. Missing points
5. Final summary
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content