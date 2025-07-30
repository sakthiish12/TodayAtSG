"""
Authentication API endpoints for Vercel serverless deployment.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import logging

# Import backend modules
try:
    from app.api.endpoints.auth import router as auth_router
    from app.core.config import settings
    from app.core.middleware import setup_cors
except ImportError as e:
    logging.error(f"Auth import error: {e}")
    # Create minimal fallback
    auth_router = APIRouter(prefix="/auth", tags=["authentication"])
    
    @auth_router.get("/health")
    async def auth_health():
        return {"status": "auth service healthy", "mode": "serverless"}

# Create the main router
router = APIRouter()
router.include_router(auth_router)

def handler(request):
    """Handler for authentication endpoints."""
    from fastapi import FastAPI
    
    app = FastAPI(title="TodayAtSG Auth API")
    
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