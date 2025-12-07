"""Chat endpoint for RAG-based Q&A."""

from fastapi import APIRouter, Depends, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.requests import ChatRequest
from app.models.responses import ChatResponse, Citation
from app.api.dependencies import (
    get_embedding_service,
    get_vector_store,
    get_llm_service,
)
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.llm import LLMService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("5/minute")
async def chat(
    request: ChatRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
    llm_service: LLMService = Depends(get_llm_service),
) -> ChatResponse:
    """Process a chat message using RAG.

    This endpoint:
    1. Embeds the user's query
    2. Retrieves relevant context from the vector store
    3. Generates a response using the LLM with retrieved context
    4. Returns the response with citations

    Rate limited to 5 requests per minute per IP.
    """
    # Validate services are configured
    if not embedding_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Embedding service not configured. Check API keys.",
        )

    if not llm_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="LLM service not configured. Check API keys.",
        )

    try:
        # Generate query embedding
        query_vector = await embedding_service.embed_query(request.query)

        # Search for relevant context
        search_results = await vector_store.search(
            query_vector=query_vector,
            limit=5,
            chapter_filter=request.chapter_filter,
            language_filter=request.language,
        )

        # Generate response with context
        answer = await llm_service.generate_response(
            query=request.query,
            context_docs=search_results,
            history=request.history,
            language=request.language,
        )

        # Extract citations from search results
        citations = [
            Citation(
                chapter_id=result["chapter_id"],
                chapter_title=result["chapter_title"],
                section_id=result["section_id"],
                section_title=result["section_title"],
                path=result["path"],
            )
            for result in search_results
            if result.get("score", 0) > 0.5  # Only cite high-relevance results
        ]

        # Remove duplicate citations
        seen = set()
        unique_citations = []
        for citation in citations:
            key = (citation.chapter_id, citation.section_id)
            if key not in seen:
                seen.add(key)
                unique_citations.append(citation)

        return ChatResponse(
            answer=answer,
            citations=unique_citations,
            model=llm_service.model_name,
            language=request.language,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}",
        )
