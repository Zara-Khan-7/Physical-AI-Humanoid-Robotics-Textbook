"""Search endpoint for content retrieval."""

from fastapi import APIRouter, Depends, HTTPException

from app.models.requests import SearchRequest
from app.models.responses import SearchResponse, SearchResult
from app.api.dependencies import get_embedding_service, get_vector_store
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
) -> SearchResponse:
    """Search for relevant content in the textbook.

    This endpoint performs semantic search to find content
    that matches the user's query.
    """
    # Validate service is configured
    if not embedding_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Embedding service not configured. Check API keys.",
        )

    try:
        # Generate query embedding
        query_vector = await embedding_service.embed_query(request.query)

        # Search vector store
        results = await vector_store.search(
            query_vector=query_vector,
            limit=request.limit,
            chapter_filter=request.chapter_filter,
            language_filter=request.language,
        )

        # Convert to response model
        search_results = [
            SearchResult(
                id=result["id"],
                score=result["score"],
                content=result["content"],
                chapter_id=result["chapter_id"],
                chapter_title=result["chapter_title"],
                section_id=result["section_id"],
                section_title=result["section_title"],
                path=result["path"],
            )
            for result in results
        ]

        return SearchResponse(
            results=search_results,
            query=request.query,
            total=len(search_results),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search: {str(e)}",
        )
