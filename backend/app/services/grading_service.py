from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def grade_answer(answer_text):

    prompt = f"""
    You are an exam evaluator.

    Evaluate this student answer.

    Give:
    1. Marks out of 10
    2. Feedback
    3. Mistakes
    4. Final summary

    Student Answer:
    {answer_text}
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