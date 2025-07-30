"""Scraping endpoints for admin management of web scraping."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Dict
import structlog

from app.db.database import get_db
from app.core.security import get_current_admin_user
from app.models.user import User
from app.services.scraping import scraping_service
from app.core.config import settings
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
logger = structlog.get_logger("scraping_api")


class ScrapingJobResponse(BaseModel):
    """Response model for scraping job."""
    job_id: str
    status: str
    message: str


class ScrapingResultResponse(BaseModel):
    """Response model for scraping results."""
    status: str
    sources_scraped: List[str]
    total_events_found: int
    events_saved: int
    duration_seconds: int
    start_time: str
    end_time: str
    error: str = None


@router.post("/run", response_model=ScrapingJobResponse)
async def run_scraping_job(
    background_tasks: BackgroundTasks,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Start a scraping job for all sources."""
    
    try:
        # Generate a simple job ID
        import uuid
        job_id = str(uuid.uuid4())
        
        # Add scraping task to background
        background_tasks.add_task(
            _run_scraping_background_task,
            job_id,
            current_admin.id
        )
        
        logger.info(
            "Scraping job started",
            job_id=job_id,
            admin_id=current_admin.id,
        )
        
        return ScrapingJobResponse(
            job_id=job_id,
            status="started",
            message="Scraping job has been started in the background"
        )
        
    except Exception as e:
        logger.error(
            "Error starting scraping job",
            admin_id=current_admin.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start scraping job"
        )


@router.post("/run-sync", response_model=ScrapingResultResponse)
async def run_scraping_sync(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Run scraping job synchronously and return results."""
    
    try:
        logger.info(
            "Starting synchronous scraping job",
            admin_id=current_admin.id,
        )
        
        # Run scraping directly
        result = await scraping_service.run_daily_scraping()
        
        logger.info(
            "Synchronous scraping job completed",
            admin_id=current_admin.id,
            status=result["status"],
            events_saved=result.get("events_saved", 0),
        )
        
        return ScrapingResultResponse(
            status=result["status"],
            sources_scraped=result.get("sources_scraped", []),
            total_events_found=result.get("total_events_found", 0),
            events_saved=result.get("events_saved", 0),
            duration_seconds=result.get("duration_seconds", 0),
            start_time=str(result.get("start_time", "")),
            end_time=str(result.get("end_time", "")),
            error=result.get("error"),
        )
        
    except ScrapingError as e:
        logger.error(
            "Scraping error in sync job",
            admin_id=current_admin.id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(
            "Unexpected error in sync scraping job",
            admin_id=current_admin.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scraping job failed"
        )


@router.get("/sources")
async def get_scraping_sources(
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Get available scraping sources with enhanced information."""
    
    try:
        # Get scraper info from service
        scraper_info = scraping_service.get_scraper_info()
        
        # Enhanced source information
        source_details = {
            "visitsingapore": {
                "display_name": "VisitSingapore",
                "description": "Official Singapore tourism events, festivals, and cultural activities",
                "category": "Tourism",
                "status": "active"
            },
            "eventbrite": {
                "display_name": "Eventbrite Singapore",
                "description": "Community events, workshops, and user-generated activities",
                "category": "Community",
                "status": "active"
            },
            "marinabaysands": {
                "display_name": "Marina Bay Sands",
                "description": "Premium entertainment, concerts, and exhibitions",
                "category": "Premium",
                "status": "active"
            },
            "sunteccity": {
                "display_name": "Suntec City",
                "description": "Shopping events, conventions, and mall activities",
                "category": "Shopping/Business",
                "status": "active"
            },
            "community_centers": {
                "display_name": "Community Centers",
                "description": "Grassroots activities, classes, and neighborhood events",
                "category": "Community",
                "status": "active"
            }
        }
        
        sources = []
        for source_name, info in scraper_info.items():
            details = source_details.get(source_name, {})
            sources.append({
                "name": source_name,
                "display_name": details.get("display_name", info["name"].title()),
                "url": info["base_url"],
                "description": details.get("description", info["description"]),
                "category": details.get("category", "General"),
                "max_events": info["max_events"],
                "status": details.get("status", "active")
            })
        
        return {
            "sources": sources,
            "total_sources": len(sources),
            "active_sources": len([s for s in sources if s["status"] == "active"]),
            "categories": list(set(s["category"] for s in sources))
        }
        
    except Exception as e:
        logger.error("Error getting scraping sources", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scraping sources"
        )


@router.post("/test/{source_name}")
async def test_scraping_source(
    source_name: str,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Test scraping from a specific source with enhanced validation and processing."""
    
    try:
        # Get available sources
        scraper_info = scraping_service.get_scraper_info()
        valid_sources = list(scraper_info.keys())
        
        if source_name not in valid_sources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source. Must be one of: {valid_sources}"
            )
        
        logger.info(
            "Testing scraping source",
            source=source_name,
            admin_id=current_admin.id,
        )
        
        # Use the service's test method for comprehensive testing
        test_result = await scraping_service.test_scraper(source_name, limit=5)
        
        logger.info(
            "Scraping source test completed",
            source=source_name,
            admin_id=current_admin.id,
            success=test_result["success"],
            events_found=test_result.get("events_found", 0),
        )
        
        return {
            "source": source_name,
            "status": "success" if test_result["success"] else "error",
            "events_found": test_result.get("events_found", 0),
            "events_processed": test_result.get("events_processed", 0),
            "sample_events": test_result.get("sample_events", []),
            "errors": test_result.get("errors", []),
            "duration_seconds": test_result.get("duration_seconds", 0),
            "message": f"Test completed for {source_name}. Found {test_result.get('events_found', 0)} events, processed {test_result.get('events_processed', 0)}."
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(
            "Unexpected error testing scraping source",
            source=source_name,
            admin_id=current_admin.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test scraping source: {source_name}"
        )


async def _run_scraping_background_task(job_id: str, admin_id: int) -> None:
    """Background task for running scraping job."""
    
    try:
        logger.info(
            "Background scraping task started",
            job_id=job_id,
            admin_id=admin_id,
        )
        
        # Run the scraping
        result = await scraping_service.run_daily_scraping()
        
        logger.info(
            "Background scraping task completed",
            job_id=job_id,
            admin_id=admin_id,
            status=result["status"],
            events_saved=result.get("events_saved", 0),
        )
        
        # TODO: Store job result in database or cache for retrieval
        # TODO: Send notification to admin user about job completion
        
    except Exception as e:
        logger.error(
            "Background scraping task failed",
            job_id=job_id,
            admin_id=admin_id,
            error=str(e),
            exc_info=True,
        )
        
        # TODO: Store error result in database or cache
        # TODO: Send error notification to admin user


@router.get("/stats")
async def get_scraping_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get scraping statistics."""
    
    try:
        from sqlalchemy import select, func
        from app.models.event import Event
        from datetime import datetime, timedelta
        
        # Get counts of scraped events by source
        scraped_events_query = select(
            Event.scraped_from,
            func.count(Event.id).label('count')
        ).where(
            Event.source == 'scraped'
        ).group_by(Event.scraped_from)
        
        result = await db.execute(scraped_events_query)
        scraped_counts = {row.scraped_from or 'unknown': row.count for row in result.all()}
        
        # Get recent scraping activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_scraped_query = select(func.count(Event.id)).where(
            Event.source == 'scraped',
            Event.created_at >= week_ago
        )
        recent_result = await db.execute(recent_scraped_query)
        recent_scraped = recent_result.scalar() or 0
        
        # Get total scraped events
        total_scraped_query = select(func.count(Event.id)).where(Event.source == 'scraped')
        total_result = await db.execute(total_scraped_query)
        total_scraped = total_result.scalar() or 0
        
        return {
            "total_scraped_events": total_scraped,
            "recent_scraped_events": recent_scraped,
            "events_by_source": scraped_counts,
            "sources_active": len([s for s in scraped_counts.keys() if s != 'unknown']),
            "last_updated": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(
            "Error getting scraping stats",
            admin_id=current_admin.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scraping statistics"
        )


@router.post("/source/{source_name}")
async def scrape_single_source(
    source_name: str,
    max_events: int = None,
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Scrape events from a specific source."""
    
    try:
        # Get available sources
        scraper_info = scraping_service.get_scraper_info()
        valid_sources = list(scraper_info.keys())
        
        if source_name not in valid_sources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid source. Must be one of: {valid_sources}"
            )
        
        # Validate max_events if provided
        if max_events is not None and (max_events < 1 or max_events > 1000):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="max_events must be between 1 and 1000"
            )
        
        logger.info(
            "Scraping single source",
            source=source_name,
            max_events=max_events,
            admin_id=current_admin.id,
        )
        
        # Run the scraping
        result = await scraping_service.scrape_source(source_name, max_events)
        
        logger.info(
            "Single source scraping completed",
            source=source_name,
            admin_id=current_admin.id,
            success=result.success,
            events_found=result.events_found,
            events_saved=result.events_saved,
        )
        
        return {
            "source": source_name,
            "status": "success" if result.success else "error",
            "events_found": result.events_found,
            "events_saved": result.events_saved,
            "errors": result.errors,
            "duration_seconds": result.duration_seconds,
            "start_time": result.start_time.isoformat(),
            "end_time": result.end_time.isoformat(),
            "message": f"Scraped {result.events_saved} events from {source_name}"
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(
            "Error scraping single source",
            source=source_name,
            admin_id=current_admin.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape source: {source_name}"
        )


@router.get("/health")
async def scraping_health_check(
    current_admin: User = Depends(get_current_admin_user)
) -> Any:
    """Health check for scraping system."""
    
    try:
        # Get basic system info
        scraper_info = scraping_service.get_scraper_info()
        
        # Simple connectivity test for each scraper
        health_results = {}
        
        for source_name in scraper_info.keys():
            try:
                # Quick test with minimal events
                test_result = await scraping_service.test_scraper(source_name, limit=1)
                health_results[source_name] = {
                    "status": "healthy" if test_result["success"] else "unhealthy",
                    "response_time": test_result.get("duration_seconds", 0),
                    "last_error": test_result.get("error", None) if not test_result["success"] else None
                }
            except Exception as e:
                health_results[source_name] = {
                    "status": "unhealthy",
                    "response_time": 0,
                    "last_error": str(e)
                }
        
        # Overall health status
        healthy_sources = len([r for r in health_results.values() if r["status"] == "healthy"])
        total_sources = len(health_results)
        
        overall_status = "healthy" if healthy_sources == total_sources else (
            "degraded" if healthy_sources > 0 else "unhealthy"
        )
        
        return {
            "overall_status": overall_status,
            "total_sources": total_sources,
            "healthy_sources": healthy_sources,
            "unhealthy_sources": total_sources - healthy_sources,
            "source_health": health_results,
            "timestamp": datetime.utcnow().isoformat(),
            "system_info": {
                "max_events_per_source": settings.SCRAPING_MAX_EVENTS_PER_SOURCE,
                "scraping_delay": settings.SCRAPING_DELAY,
                "max_retries": settings.SCRAPING_MAX_RETRIES,
                "timeout": settings.SCRAPING_TIMEOUT
            }
        }
        
    except Exception as e:
        logger.error(
            "Error in scraping health check",
            admin_id=current_admin.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )