from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = Field(default="DocExtractPlatform", env="APP_NAME")
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=True, env="DEBUG")

    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/doc_extraction",
        env="DATABASE_URL"
    )

    # OpenAI / LLM
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o", env="LLM_MODEL")

    # OCR
    ocr_engine: str = Field(default="tesseract", env="OCR_ENGINE")  # tesseract | paddleocr

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
