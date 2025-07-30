"""
Users API endpoints for Vercel serverless deployment.
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
    from app.api.endpoints.users import router as users_router
    from app.core.config import settings
except ImportError as e:
    logging.error(f"Users import error: {e}")
    # Create minimal fallback
    users_router = APIRouter(prefix="/users", tags=["users"])
    
    @users_router.get("/health")
    async def users_health():
        return {"status": "users service healthy", "mode": "serverless"}

# Create the main router
router = APIRouter()
router.include_router(users_router)

def handler(request):
    """Handler for users endpoints."""
    from fastapi import FastAPI
    
    app = FastAPI(title="TodayAtSG Users API")
    
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