from typing import List

from pydantic import BaseModel, Field

from gemini_client import generate_structured

from schemas import (
    QuizQuestion,
    QuizResponse,
)


class GeminiQuiz(BaseModel):

    questions: List[QuizQuestion] = Field(
        min_length=3,
        max_length=3,
    )


async def generate_quiz(
    passage: str,
) -> QuizResponse:

    prompt = f"""
Create exactly three multiple-choice
questions from the passage below.

Rules:

- Create exactly 3 questions.
- Every question must have exactly
  4 different options.
- Exactly one option must be correct.
- correct_answer must exactly match
  one of the option strings.
- Questions must be based only on
  the supplied passage.
- Do not create unrelated questions.
- Include a short explanation for
  every correct answer.

PASSAGE:

{passage}
"""

    quiz = generate_structured(
        prompt,
        GeminiQuiz,

        system_instruction=(
            "You are EduGenie's quiz "
            "generation module. "
            "Create high-quality educational "
            "multiple-choice questions."
        ),

        temperature=0.25,

        max_output_tokens=1800,
    )

    return QuizResponse(
        questions=quiz.questions
    )