from typing import TypeVar

from google import genai
from google.genai import errors
from pydantic import BaseModel

from config import settings


ModelType = TypeVar("ModelType", bound=BaseModel)


class GeminiServiceError(RuntimeError):
    """Raised when Gemini cannot serve a generation request."""


_client = genai.Client(api_key=settings.gemini_api_key)


def _generate_content(prompt: str, config: dict):
    try:
        return _client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=config,
        )
    except errors.APIError as error:
        raise GeminiServiceError(
            "Gemini is temporarily unavailable. Please try again shortly."
        ) from error


def generate_text(
    prompt: str,
    *,
    system_instruction: str,
    temperature: float,
    max_output_tokens: int,
) -> str:
    response = _generate_content(
        prompt,
        {
            "system_instruction": system_instruction,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        },
    )
    return response.text or ""


def generate_structured(
    prompt: str,
    response_model: type[ModelType],
    *,
    system_instruction: str,
    temperature: float,
    max_output_tokens: int,
) -> ModelType:
    response = _generate_content(
        prompt,
        {
            "system_instruction": system_instruction,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
            "response_mime_type": "application/json",
            "response_schema": response_model,
        },
    )
    return response_model.model_validate_json(response.text)
