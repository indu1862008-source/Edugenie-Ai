from typing import List

from pydantic import BaseModel, Field

from gemini_client import generate_structured

from schemas import (
    LearningPathResponse,
    LearningStep,
)


class GeminiLearningPath(BaseModel):

    steps: List[LearningStep] = Field(
        min_length=3,
        max_length=8,
    )

    study_tips: List[str] = Field(
        min_length=3,
        max_length=8,
    )


async def get_learning_recommendations(
    topic: str,
    level: str,
) -> LearningPathResponse:

    prompt = f"""
Create a structured learning path
for the following topic:

TOPIC:
{topic}

LEARNER LEVEL:
{level}

The path should progress from
foundational concepts toward more
advanced concepts.

For every stage provide:

- stage: short stage name
- topics: concrete concepts to study
- estimated_time: realistic time estimate
- resources: useful resource types
  or search phrases

Also provide 3-8 practical study tips.

Do not invent specific URLs.

Make the plan adaptable.
"""

    result = generate_structured(
        prompt,
        GeminiLearningPath,

        system_instruction=(
            "You are an educational "
            "curriculum assistant. "
            "Create practical and logically "
            "sequenced study plans."
        ),

        temperature=0.35,

        max_output_tokens=2200,
    )

    return LearningPathResponse(
        topic=topic,
        level=level,
        steps=result.steps,
        study_tips=result.study_tips,
    )