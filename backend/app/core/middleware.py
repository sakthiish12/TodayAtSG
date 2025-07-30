"""
Middleware for error handling, logging, and request processing.
"""

import time
import uuid
import traceback
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog
from sqlalchemy.exc import IntegrityError, OperationalError
from pydantic import ValidationError

from app.core.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = structlog.get_logger("request")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to headers
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        self.logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=client_ip,
            user_agent=user_agent,
            path_params=request.path_params,
            query_params=dict(request.query_params),
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            self.logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=round(process_time, 4),
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            self.logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                process_time=round(process_time, 4),
                error=str(exc),
                exc_info=True,
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions and returning appropriate error responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = structlog.get_logger("error_handler")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
            
        except HTTPException as exc:
            # FastAPI HTTPExceptions are already handled by FastAPI
            raise
            
        except ValidationError as exc:
            # Pydantic validation errors
            request_id = getattr(request.state, 'request_id', 'unknown')
            self.logger.warning(
                "Validation error",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                errors=exc.errors(),
            )
            
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Validation Error",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "request_id": request_id,
                }
            )
            
        except IntegrityError as exc:
            # Database integrity constraint violations
            request_id = getattr(request.state, 'request_id', 'unknown')
            self.logger.warning(
                "Database integrity error",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(exc.orig) if hasattr(exc, 'orig') else str(exc),
            )
            
            return JSONResponse(
                status_code=409,
                content={
                    "error": "Conflict",
                    "message": "Data integrity constraint violation",
                    "request_id": request_id,
                }
            )
            
        except OperationalError as exc:
            # Database connection or operational errors
            request_id = getattr(request.state, 'request_id', 'unknown')
            self.logger.error(
                "Database operational error",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(exc.orig) if hasattr(exc, 'orig') else str(exc),
            )
            
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service Unavailable",
                    "message": "Database service is temporarily unavailable",
                    "request_id": request_id,
                }
            )
            
        except Exception as exc:
            # Catch-all for unexpected errors
            request_id = getattr(request.state, 'request_id', 'unknown')
            self.logger.error(
                "Unexpected error",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(exc),
                traceback=traceback.format_exc(),
                exc_info=True,
            )
            
            # In production, don't expose internal error details
            if settings.DEBUG:
                error_detail = str(exc)
                traceback_info = traceback.format_exc()
            else:
                error_detail = "An internal server error occurred"
                traceback_info = None
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": error_detail,
                    "request_id": request_id,
                    "traceback": traceback_info,
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self' https://api.stripe.com; "
                "frame-src 'none'"
            ),
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_counts: Dict[str, Dict[str, Any]] = {}
        self.logger = structlog.get_logger("rate_limit")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        self.request_counts = {
            ip: data for ip, data in self.request_counts.items()
            if current_time - data.get("first_request", 0) < 60
        }
        
        # Initialize or update request count for this IP
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {
                "count": 1,
                "first_request": current_time,
            }
        else:
            self.request_counts[client_ip]["count"] += 1
        
        # Check rate limits
        count = self.request_counts[client_ip]["count"]
        is_auth_endpoint = request.url.path.startswith("/api/auth/")
        
        # Different limits for auth vs regular endpoints
        rate_limit = (
            settings.AUTH_RATE_LIMIT_REQUESTS_PER_MINUTE
            if is_auth_endpoint
            else settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        )
        
        if count > rate_limit:
            self.logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                path=request.url.path,
                count=count,
                limit=rate_limit,
                is_auth_endpoint=is_auth_endpoint,
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded. Maximum {rate_limit} requests per minute.",
                    "retry_after": 60,
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, rate_limit - count))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response


# Helper function to get request ID from current request
def get_request_id(request: Request) -> str:
    """Get the current request ID."""
    return getattr(request.state, 'request_id', 'unknown')


# Exception handlers for specific error types
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    request_id = get_request_id(request)
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "request_id": request_id,
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    request_id = get_request_id(request)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.detail,
            "request_id": request_id,
        }
    )