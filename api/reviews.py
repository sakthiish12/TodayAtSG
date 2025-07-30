"""
Reviews API endpoints for Vercel serverless deployment.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging

# Import backend modules
try:
    from app.api.endpoints.reviews import router as reviews_router
    from app.core.config import settings
except ImportError as e:
    logging.error(f"Reviews import error: {e}")
    # Create minimal fallback
    reviews_router = APIRouter(prefix="/reviews", tags=["reviews"])
    
    @reviews_router.get("/health")
    async def reviews_health():
        return {"status": "reviews service healthy", "mode": "serverless"}

# Create the main router
router = APIRouter()
router.include_router(reviews_router)

def handler(request):
    """Handler for reviews endpoints."""
    from fastapi import FastAPI
    
    app = FastAPI(title="TodayAtSG Reviews API")
    
    # Add CORS
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(router)
    return app

# Export for Vercel
def main(request):
    return handler(request)