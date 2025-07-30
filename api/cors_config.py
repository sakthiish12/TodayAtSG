"""
CORS configuration for Vercel serverless deployment.
Handles cross-origin requests for the TodayAtSG application.
"""

import os
from typing import List, Union
from fastapi.middleware.cors import CORSMiddleware

def get_cors_origins() -> List[str]:
    """
    Get allowed CORS origins based on environment.
    """
    # Production origins
    production_origins = [
        "https://todayatsg.com",
        "https://www.todayatsg.com",
        "https://todayatsg.vercel.app",
    ]
    
    # Development origins
    development_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]
    
    # Get environment
    environment = os.getenv("ENVIRONMENT", "production").lower()
    vercel_env = os.getenv("VERCEL_ENV", "production").lower()
    
    # Base origins
    if environment == "development" or vercel_env == "development":
        allowed_origins = production_origins + development_origins
    else:
        allowed_origins = production_origins.copy()
    
    # Add custom origins from environment variable
    custom_origins = os.getenv("ALLOWED_ORIGINS", "")
    if custom_origins:
        custom_list = [origin.strip() for origin in custom_origins.split(",")]
        allowed_origins.extend(custom_list)
    
    # Add Vercel preview URLs
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        allowed_origins.append(f"https://{vercel_url}")
    
    # Add Vercel branch URLs
    vercel_git_commit_ref = os.getenv("VERCEL_GIT_COMMIT_REF")
    if vercel_git_commit_ref and vercel_git_commit_ref != "main":
        # Add branch-specific preview URL
        branch_url = f"https://todayatsg-git-{vercel_git_commit_ref}-your-team.vercel.app"
        allowed_origins.append(branch_url)
    
    # Remove duplicates and return
    return list(set(allowed_origins))

def get_cors_methods() -> List[str]:
    """Get allowed CORS methods."""
    custom_methods = os.getenv("ALLOWED_METHODS", "")
    if custom_methods:
        return [method.strip() for method in custom_methods.split(",")]
    
    return ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"]

def get_cors_headers() -> List[str]:
    """Get allowed CORS headers."""
    custom_headers = os.getenv("ALLOWED_HEADERS", "")
    if custom_headers and custom_headers != "*":
        return [header.strip() for header in custom_headers.split(",")]
    
    return [
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-API-Key",
        "Cache-Control",
        "Pragma",
        "User-Agent",
    ]

def configure_cors(app, allow_credentials: bool = True):
    """
    Configure CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        allow_credentials: Whether to allow credentials in requests
    """
    origins = get_cors_origins()
    methods = get_cors_methods()
    headers = get_cors_headers()
    
    # Determine if we should allow all headers
    allow_headers = ["*"] if os.getenv("ALLOWED_HEADERS") == "*" else headers
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=methods,
        allow_headers=allow_headers,
        expose_headers=[
            "X-Total-Count",
            "X-Page-Count",
            "X-Page-Size",
            "X-Current-Page",
            "X-Rate-Limit-Limit",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
        ],
        max_age=86400,  # Cache preflight requests for 24 hours
    )
    
    return app

def get_cors_config() -> dict:
    """
    Get CORS configuration as a dictionary.
    Useful for debugging and logging.
    """
    return {
        "origins": get_cors_origins(),
        "methods": get_cors_methods(),
        "headers": get_cors_headers(),
        "credentials": True,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "vercel_env": os.getenv("VERCEL_ENV", "production"),
        "vercel_url": os.getenv("VERCEL_URL"),
    }

# Pre-flight response headers for manual CORS handling
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",  # Will be set dynamically
    "Access-Control-Allow-Methods": ", ".join(get_cors_methods()),
    "Access-Control-Allow-Headers": ", ".join(get_cors_headers()),
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Max-Age": "86400",
}

def create_cors_response(origin: str = None) -> dict:
    """
    Create CORS response headers for manual handling.
    
    Args:
        origin: The requesting origin
        
    Returns:
        Dictionary of CORS headers
    """
    headers = CORS_HEADERS.copy()
    
    if origin and origin in get_cors_origins():
        headers["Access-Control-Allow-Origin"] = origin
    elif os.getenv("ENVIRONMENT") == "development":
        headers["Access-Control-Allow-Origin"] = "*"
    
    return headers