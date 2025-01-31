from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    GEMINI_API_KEY: str
    ALLOWED_ORIGINS: List[str]


settings = Settings()
