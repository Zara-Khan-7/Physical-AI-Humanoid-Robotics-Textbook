"""Health check endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.models.responses import HealthResponse, HealthStatus
from app.api.dependencies import get_vector_store, get_embedding_service, get_llm_service
from app.services.vector_store import VectorStoreService
from app.services.embeddings import EmbeddingService
from app.services.llm import LLMService

router = APIRouter()


class DetailedHealthResponse(BaseModel):
    """Detailed health response with metrics."""

    status: str
    services: HealthStatus
    metrics: dict


@router.get("/health", response_model=HealthResponse)
async def health_check(
    vector_store: VectorStoreService = Depends(get_vector_store),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> HealthResponse:
    """Check service health and dependency connectivity.

    This endpoint is used by deployment platforms for health checks.
    Returns quickly with basic status.
    """
    services = HealthStatus()

    # Check Qdrant connection
    try:
        if await vector_store.health_check():
            services.qdrant = "connected"
    except Exception:
        services.qdrant = "disconnected"

    # Check embedding service (Google AI)
    try:
        if embedding_service.is_configured():
            services.embeddings = "available"
            services.gemini = "available"
    except Exception:
        services.embeddings = "unavailable"
        services.gemini = "unavailable"

    # Determine overall status
    if services.qdrant == "connected" and services.embeddings == "available":
        status = "healthy"
    elif services.qdrant == "connected" or services.embeddings == "available":
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(status=status, services=services)


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(
    vector_store: VectorStoreService = Depends(get_vector_store),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> DetailedHealthResponse:
    """Detailed health check with metrics.

    Use this for debugging and monitoring dashboards.
    May be slower as it performs additional checks.
    """
    services = HealthStatus()
    metrics = {
        "qdrant": {},
        "embeddings": {},
        "llm": {},
    }

    # Check Qdrant connection and get collection info
    try:
        if await vector_store.health_check():
            services.qdrant = "connected"
            info = await vector_store.get_collection_info()
            metrics["qdrant"] = {
                "collection": info.get("name", "unknown"),
                "vectors_count": info.get("vectors_count", 0),
                "points_count": info.get("points_count", 0),
            }
    except Exception as e:
        services.qdrant = "disconnected"
        metrics["qdrant"] = {"error": str(e)}

    # Check embedding service
    try:
        if embedding_service.is_configured():
            services.embeddings = "available"
            metrics["embeddings"] = {
                "model": embedding_service.model,
                "dimensions": embedding_service.dimensions,
            }
    except Exception as e:
        services.embeddings = "unavailable"
        metrics["embeddings"] = {"error": str(e)}

    # Check LLM service
    try:
        if llm_service.is_configured():
            services.gemini = "available"
            metrics["llm"] = {
                "model": llm_service.model_name,
            }
    except Exception as e:
        services.gemini = "unavailable"
        metrics["llm"] = {"error": str(e)}

    # Determine overall status
    if services.qdrant == "connected" and services.embeddings == "available":
        status = "healthy"
    elif services.qdrant == "connected" or services.embeddings == "available":
        status = "degraded"
    else:
        status = "unhealthy"

    return DetailedHealthResponse(
        status=status,
        services=services,
        metrics=metrics,
    )


@router.get("/ready")
async def readiness_check(
    vector_store: VectorStoreService = Depends(get_vector_store),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> dict:
    """Kubernetes-style readiness probe.

    Returns 200 if the service is ready to accept traffic.
    Returns 503 if not ready.
    """
    try:
        qdrant_ok = await vector_store.health_check()
        embeddings_ok = embedding_service.is_configured()

        if qdrant_ok and embeddings_ok:
            return {"ready": True}
        else:
            return {"ready": False, "reason": "dependencies not ready"}
    except Exception as e:
        return {"ready": False, "reason": str(e)}


@router.get("/live")
async def liveness_check() -> dict:
    """Kubernetes-style liveness probe.

    Returns 200 if the service is alive.
    This should always return quickly.
    """
    return {"alive": True}
