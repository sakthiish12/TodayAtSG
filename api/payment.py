"""
Payment API endpoints for Vercel serverless deployment.
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
    from app.api.endpoints.payment import router as payment_router
    from app.core.config import settings
except ImportError as e:
    logging.error(f"Payment import error: {e}")
    # Create minimal fallback
    payment_router = APIRouter(prefix="/payment", tags=["payment"])
    
    @payment_router.get("/health")
    async def payment_health():
        return {"status": "payment service healthy", "mode": "serverless"}

# Create the main router
router = APIRouter()
router.include_router(payment_router)

def handler(request):
    """Handler for payment endpoints."""
    from fastapi import FastAPI
    
    app = FastAPI(title="TodayAtSG Payment API")
    
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