"""Vector store service for Qdrant operations."""

from typing import Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
import uuid


class VectorStoreService:
    """Service for vector storage and retrieval using Qdrant."""

    def __init__(
        self,
        url: str,
        api_key: str = "",
        collection_name: str = "textbook_chunks",
        vector_size: int = 768,
    ):
        """Initialize the vector store service.

        Args:
            url: Qdrant server URL
            api_key: Qdrant API key (optional for local)
            collection_name: Name of the collection
            vector_size: Dimension of vectors
        """
        self.url = url
        self.collection_name = collection_name
        self.vector_size = vector_size

        # Initialize client
        if api_key:
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            self.client = QdrantClient(url=url)

    async def health_check(self) -> bool:
        """Check if Qdrant is accessible."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

    async def ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert_chunks(
        self,
        chunks: list[dict[str, Any]],
        vectors: list[list[float]],
    ) -> int:
        """Insert or update content chunks with their vectors.

        Args:
            chunks: List of chunk metadata dictionaries
            vectors: Corresponding embedding vectors

        Returns:
            Number of points upserted
        """
        await self.ensure_collection()

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=chunk,
            )
            for chunk, vector in zip(chunks, vectors)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        return len(points)

    async def search(
        self,
        query_vector: list[float],
        limit: int = 5,
        chapter_filter: str | None = None,
        language_filter: str = "en",
    ) -> list[dict[str, Any]]:
        """Search for similar content chunks.

        Args:
            query_vector: Query embedding vector
            limit: Maximum results to return
            chapter_filter: Optional chapter ID filter
            language_filter: Language filter (default: en)

        Returns:
            List of search results with metadata and scores
        """
        # Build filter conditions
        filter_conditions = [
            FieldCondition(
                key="language",
                match=MatchValue(value=language_filter),
            )
        ]

        if chapter_filter:
            filter_conditions.append(
                FieldCondition(
                    key="chapter_id",
                    match=MatchValue(value=chapter_filter),
                )
            )

        search_filter = Filter(must=filter_conditions) if filter_conditions else None

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=search_filter,
            with_payload=True,
        )

        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "content": hit.payload.get("content", ""),
                "chapter_id": hit.payload.get("chapter_id", ""),
                "chapter_title": hit.payload.get("chapter_title", ""),
                "section_id": hit.payload.get("section_id", ""),
                "section_title": hit.payload.get("section_title", ""),
                "path": hit.payload.get("path", ""),
            }
            for hit in results
        ]

    async def delete_by_chapter(self, chapter_id: str) -> None:
        """Delete all chunks for a specific chapter.

        Args:
            chapter_id: Chapter ID to delete
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="chapter_id",
                        match=MatchValue(value=chapter_id),
                    )
                ]
            ),
        )

    async def get_collection_info(self) -> dict[str, Any]:
        """Get collection statistics."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
            }
        except Exception:
            return {"name": self.collection_name, "vectors_count": 0, "points_count": 0}
