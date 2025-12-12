"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.api.routes import health, chat, search, auth, agents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    settings = get_settings()
    print(f"Starting server on {settings.host}:{settings.port}")
    print(f"CORS origins: {settings.cors_origins_list}")
    yield
    # Shutdown
    print("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="AI-Native Textbook RAG API",
        description="Backend API for the Physical AI & Humanoid Robotics textbook chatbot",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add rate limiter
    app.state.limiter = limiter

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
    app.include_router(search.router, prefix="/api/v1", tags=["Search"])
    app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
    app.include_router(agents.router, prefix="/api/v1", tags=["Agents"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
