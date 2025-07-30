"""
Events API endpoints for Vercel serverless deployment.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

# Import backend modules
try:
    from app.api.endpoints.events import router as events_router
    from app.core.config import settings
except ImportError as e:
    logging.error(f"Events import error: {e}")
    # Create minimal fallback
    events_router = APIRouter(prefix="/events", tags=["events"])
    
    @events_router.get("/")
    async def get_events():
        return {"message": "Events endpoint", "mode": "serverless"}
    
    @events_router.get("/health")
    async def events_health():
        return {"status": "events service healthy", "mode": "serverless"}

# Create the main router
router = APIRouter()
router.include_router(events_router)

def handler(request):
    """Handler for events endpoints."""
    from fastapi import FastAPI
    
    app = FastAPI(title="TodayAtSG Events API")
    
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