from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/incidents"
    REDIS_URL: str = "redis://redis:6379/0"
    ENVIRONMENT: str = "development"
    AI_PROVIDER: str = "gemini"  # "gemini" or "groq"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
