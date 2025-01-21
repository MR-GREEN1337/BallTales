from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    GEMINI_API_KEY: str
    DATABASE_URL: str


settings = Settings()
