"""Request models for API endpoints."""

from typing import Literal
from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    """A message in conversation history."""

    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=5000)


class ChatRequest(BaseModel):
    """Request body for POST /api/v1/chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000, description="User's question")
    session_id: str = Field(..., description="Client-generated session identifier")
    context: str | None = Field(
        None, max_length=1000, description="Optional selected text context"
    )
    history: list[HistoryMessage] | None = Field(
        None, max_length=10, description="Previous messages (max 10)"
    )
    language: Literal["en", "ur"] = Field("en", description="Preferred response language")


class SearchRequest(BaseModel):
    """Query parameters for GET /api/v1/search endpoint."""

    q: str = Field(..., min_length=2, max_length=500, description="Search query")
    limit: int = Field(5, ge=1, le=20, description="Max results")
    chapter: str | None = Field(None, description="Filter by chapter ID")
    language: Literal["en", "ur"] = Field("en", description="Content language filter")
