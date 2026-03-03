import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "HarborGuard AI"
    # In a real app we'd load this from an uncommitted env file
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost:5432/harborguard"
    
    # Gemini Configuration
    GEMINI_API_KEY: str = "MOCK_API_KEY"  # Override in .env
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_TOKENS: int = 2048

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
