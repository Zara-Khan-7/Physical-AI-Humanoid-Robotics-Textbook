"""Embedding service for Google text-embedding-004."""

import google.generativeai as genai
from typing import Literal


class EmbeddingService:
    """Service for generating text embeddings using Google AI."""

    def __init__(
        self,
        api_key: str,
        model: str = "models/text-embedding-004",
        dimensions: int = 768,
    ):
        """Initialize the embedding service.

        Args:
            api_key: Google AI API key
            model: Embedding model name
            dimensions: Output vector dimensions (768, 1536, or 3072)
        """
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions

        if api_key:
            genai.configure(api_key=api_key)

    def is_configured(self) -> bool:
        """Check if the service is properly configured."""
        return bool(self.api_key)

    async def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a query (optimized for retrieval).

        Args:
            text: Query text to embed

        Returns:
            Vector embedding as list of floats
        """
        return await self._embed(text, task_type="RETRIEVAL_QUERY")

    async def embed_document(self, text: str) -> list[float]:
        """Generate embedding for a document (optimized for storage).

        Args:
            text: Document text to embed

        Returns:
            Vector embedding as list of floats
        """
        return await self._embed(text, task_type="RETRIEVAL_DOCUMENT")

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed

        Returns:
            List of vector embeddings
        """
        embeddings = []
        for text in texts:
            embedding = await self.embed_document(text)
            embeddings.append(embedding)
        return embeddings

    async def _embed(
        self,
        text: str,
        task_type: Literal["RETRIEVAL_QUERY", "RETRIEVAL_DOCUMENT"] = "RETRIEVAL_QUERY",
    ) -> list[float]:
        """Generate embedding with specified task type.

        Args:
            text: Text to embed
            task_type: Type of embedding task

        Returns:
            Vector embedding as list of floats
        """
        if not self.is_configured():
            raise ValueError("Embedding service not configured: missing API key")

        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type=task_type,
            output_dimensionality=self.dimensions,
        )

        return result["embedding"]
