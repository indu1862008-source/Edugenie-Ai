from gemini_client import generate_text


async def answer_question(
    question: str,
) -> str:

    prompt = f"""
Answer the following academic or
general-knowledge question for a student.

QUESTION:
{question}

Requirements:

- Give a direct answer first.
- Explain the answer in simple language.
- Include reasoning or useful context.
- Use short paragraphs or bullets when useful.
- Do not invent citations.
- If something is uncertain, clearly say so.
"""

    return generate_text(
        prompt,

        system_instruction=(
            "You are EduGenie, a patient "
            "educational assistant. "
            "Prioritize correctness, clarity, "
            "and age-appropriate explanations."
        ),

        temperature=0.3,

        max_output_tokens=900,
    )