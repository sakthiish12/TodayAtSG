"""
Main API handler for Vercel serverless deployment.
This file serves as the entry point for all API requests.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import the main FastAPI app from backend
try:
    from app.main import create_application
    from app.core.config import settings
except ImportError as e:
    # Fallback for serverless environment
    logging.error(f"Import error: {e}")
    
    # Create a minimal FastAPI app as fallback
    app = FastAPI(
        title="TodayAtSG API",
        version="1.0.0",
        description="Singapore Events Map Website API"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "TodayAtSG API - Serverless Mode"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "mode": "serverless"}
else:
    # Use the main application
    app = create_application()

# Vercel serverless function handler
def handler(request: Request):
    """
    Main handler for Vercel serverless deployment.
    This function will be called for all API requests.
    """
    return app

# Export the app for Vercel
def main(request):
    """Entry point for Vercel serverless functions."""
    return handler(request)

# For direct running (development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)