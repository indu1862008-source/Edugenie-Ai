from functools import lru_cache

from config import settings
from gemini_client import generate_text


# ---------------------------------------------------------
# Load LaMini lazily
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def _load_local_pipeline():

    from transformers import pipeline

    return pipeline(
        "text2text-generation",
        model=settings.local_model_name,
        device=-1,
    )


# ---------------------------------------------------------
# Local explanation
# ---------------------------------------------------------

def _local_explain(
    topic: str,
) -> str:

    pipe = _load_local_pipeline()

    prompt = (
        "Explain this topic to a beginner "
        "using simple language, a short example, "
        "and three key points.\n\n"
        f"Topic: {topic}"
    )

    result = pipe(
        prompt,
        max_new_tokens=(
            settings.local_model_max_new_tokens
        ),
        do_sample=False,
    )

    return result[0][
        "generated_text"
    ].strip()


# ---------------------------------------------------------
# Public explanation function
# ---------------------------------------------------------

async def explain_concept(
    topic: str,
) -> str:

    provider = (
        settings.explanation_provider
        .lower()
    )

    # Local mode
    if provider in {
        "local",
        "auto",
    }:

        try:

            return _local_explain(
                topic
            )

        except Exception:

            if provider == "local":
                raise

    # Gemini fallback
    prompt = f"""
Explain the following educational
concept to a learner who may be
completely new to it.

TOPIC:
{topic}

Structure your answer as:

1. Simple definition
2. How it works
3. Easy example
4. Three key points to remember
"""

    return generate_text(
        prompt,

        system_instruction=(
            "You are EduGenie's "
            "concept-explanation module. "
            "Use concise, beginner-friendly "
            "educational language."
        ),

        temperature=0.3,

        max_output_tokens=1000,
    )