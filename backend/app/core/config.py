"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Google AI API
    google_api_key: str = ""

    # Qdrant Vector Database
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "textbook_chunks"

    # Model Configuration
    embedding_model: str = "models/text-embedding-004"
    embedding_dim: int = 768
    llm_model: str = "models/gemini-flash-latest"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS - Frontend URLs (comma-separated)
    cors_origins: str = "http://localhost:3000,http://localhost:3001,https://frontend-hr4ggbpzj-zara-yousuf-khans-projects.vercel.app,https://physical-ai-textbook.vercel.app"

    # Rate Limiting
    rate_limit_chat: str = "5/minute"
    rate_limit_search: str = "20/minute"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
