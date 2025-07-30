from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import structlog

from app.core.config import settings
from app.api.api import api_router
from app.db.database import engine
from app.db.base import Base
from app.core.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logging.info("Starting up TodayAtSG API...")
    
    # Create database tables
    # Note: In production, use Alembic migrations instead
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    logging.info("Shutting down TodayAtSG API...")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Singapore Events Map Website API - Discover amazing events happening in Singapore",
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # Add middleware in correct order (reverse order due to LIFO stack)
    
    # Security headers (outermost)
    if not settings.DEBUG:
        app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting
    app.add_middleware(RateLimitMiddleware)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    # Add trusted host middleware for security
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["todayatsg.com", "*.todayatsg.com", "*.vercel.app"]
        )
    
    # Error handling middleware
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Request logging (innermost, closest to the application)
    app.add_middleware(RequestLoggingMiddleware)

    # Include API router
    app.include_router(api_router, prefix="/api")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to TodayAtSG API",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs_url": "/api/docs" if settings.DEBUG else None,
            "health_check": "/health"
        }

    return app


# Create the FastAPI application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )