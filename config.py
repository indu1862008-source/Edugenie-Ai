from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # Application
    app_name: str = "EduGenie"

    host: str = "127.0.0.1"

    port: int = 8000

    reload: bool = True

    # Gemini
    gemini_api_key: str = ""

    gemini_model: str = "gemini-3.5-flash-lite"

    # Explanation provider
    #
    # gemini = Gemini only
    # local  = LaMini only
    # auto   = LaMini first, Gemini fallback
    explanation_provider: str = "gemini"

    # Local LaMini model
    local_model_name: str = (
        "MBZUAI/LaMini-Flan-T5-783M"
    )

    local_model_max_new_tokens: int = 220

    # Input limits
    max_input_chars: int = 20000

    max_quiz_chars: int = 12000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:

    return Settings()


settings = get_settings()