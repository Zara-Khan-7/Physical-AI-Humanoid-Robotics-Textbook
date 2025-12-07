"""Response models for API endpoints."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A source citation in chatbot response."""

    chapter_id: str = Field(..., description="Chapter identifier")
    chapter_title: str = Field(..., description="Chapter title")
    section_id: str = Field(..., description="Section identifier")
    section_title: str = Field(..., description="Section title")
    path: str = Field(..., description="URL path to source section")


class ChatResponse(BaseModel):
    """Response body for POST /api/v1/chat endpoint."""

    answer: str = Field(..., description="Generated response")
    citations: list[Citation] = Field(default_factory=list)
    model: str = Field(..., description="Model used for generation")
    language: str = Field(default="en", description="Response language")


class SearchResult(BaseModel):
    """A single search result."""

    id: str = Field(..., description="Result ID")
    score: float = Field(..., description="Relevance score")
    content: str = Field(..., description="Content excerpt")
    chapter_id: str = Field(..., description="Chapter identifier")
    chapter_title: str = Field(..., description="Chapter title")
    section_id: str = Field(..., description="Section identifier")
    section_title: str = Field(..., description="Section title")
    path: str = Field(..., description="File path")


class SearchResponse(BaseModel):
    """Response body for POST /api/v1/search endpoint."""

    results: list[SearchResult]
    total: int
    query: str


class HealthStatus(BaseModel):
    """Service health status."""

    qdrant: Literal["connected", "disconnected"] = "disconnected"
    gemini: Literal["available", "unavailable"] = "unavailable"
    embeddings: Literal["available", "unavailable"] = "unavailable"


class HealthResponse(BaseModel):
    """Response body for GET /api/v1/health endpoint."""

    status: Literal["healthy", "degraded", "unhealthy"]
    services: HealthStatus = Field(default_factory=HealthStatus)


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: dict | None = None
