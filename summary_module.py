from gemini_client import generate_text


async def summarize_text(
    text: str,
) -> str:

    prompt = f"""
Summarize the educational text below
for quick revision.

Requirements:

- Preserve the important facts.
- Preserve important relationships
  between ideas.
- Remove repetition and filler.
- Use a short overview.
- Then provide 4-8 key points
  when appropriate.
- Do not introduce information
  that is not supported by the text.

TEXT:

{text}
"""

    return generate_text(
        prompt,

        system_instruction=(
            "You are EduGenie's concise "
            "academic summarization module."
        ),

        temperature=0.25,

        max_output_tokens=1200,
    )