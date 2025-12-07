"""Rate limiting configuration using SlowAPI."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime


# Create limiter with IP-based rate limiting
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle rate limit exceeded errors with standard error response."""
    retry_after = exc.detail.split("per")[0].strip() if exc.detail else "60"

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": f"Too many requests. Please try again in {retry_after}.",
            "timestamp": datetime.utcnow().isoformat(),
            "details": {"retry_after": retry_after},
        },
        headers={"Retry-After": retry_after},
    )


# Rate limit decorators for different endpoints
def chat_rate_limit():
    """Rate limit for chat endpoint: 5 requests per minute."""
    return limiter.limit("5/minute")


def search_rate_limit():
    """Rate limit for search endpoint: 20 requests per minute."""
    return limiter.limit("20/minute")
