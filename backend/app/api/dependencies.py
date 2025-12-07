"""Shared dependencies for API routes."""

from functools import lru_cache
from app.core.config import get_settings, Settings
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.llm import LLMService


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    settings = get_settings()
    return EmbeddingService(
        api_key=settings.google_api_key,
        model=settings.embedding_model,
        dimensions=settings.embedding_dim,
    )


@lru_cache
def get_vector_store() -> VectorStoreService:
    """Get cached vector store service instance."""
    settings = get_settings()
    return VectorStoreService(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection,
    )


@lru_cache
def get_llm_service() -> LLMService:
    """Get cached LLM service instance."""
    settings = get_settings()
    return LLMService(
        api_key=settings.google_api_key,
        model=settings.llm_model,
    )


def get_settings_dep() -> Settings:
    """Get settings as a dependency."""
    return get_settings()
