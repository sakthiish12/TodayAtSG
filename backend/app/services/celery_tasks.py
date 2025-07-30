"""
Celery background tasks for web scraping automation.

This module provides scheduled scraping tasks with retry logic, monitoring,
and error handling for TodayAtSG event data collection.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import structlog
from celery import Celery
from celery.schedules import crontab
import pytz

from app.core.config import settings
from app.services.scrapers import (
    VisitSingaporeScraper,
    EventbriteScraper,
    MarinaBayScandsScraper,
    SuntecCityScraper,
    CommunityCentersScraper,
    EventDataProcessor
)

logger = structlog.get_logger("celery_tasks")
singapore_tz = pytz.timezone('Asia/Singapore')

# Create Celery instance
celery_app = Celery(
    "todayatsg_scraper",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.services.celery_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Singapore',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes
    task_soft_time_limit=1500,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_heartbeat=False,
    worker_heartbeat_interval=30,
    task_routes={
        'app.services.celery_tasks.scrape_source': {'queue': 'scraping'},
        'app.services.celery_tasks.daily_scraping_job': {'queue': 'scraping'},
        'app.services.celery_tasks.cleanup_old_events': {'queue': 'maintenance'},
    },
    beat_schedule={
        'daily-morning-scraping': {
            'task': 'app.services.celery_tasks.daily_scraping_job',
            'schedule': crontab(hour=7, minute=0),  # 7 AM SGT daily
            'options': {'queue': 'scraping'}
        },
        'evening-update-scraping': {
            'task': 'app.services.celery_tasks.daily_scraping_job', 
            'schedule': crontab(hour=19, minute=0),  # 7 PM SGT daily
            'options': {'queue': 'scraping'}
        },
        'cleanup-old-events': {
            'task': 'app.services.celery_tasks.cleanup_old_events',
            'schedule': crontab(hour=2, minute=0),  # 2 AM SGT daily
            'options': {'queue': 'maintenance'}
        },
        'weekly-full-scraping': {
            'task': 'app.services.celery_tasks.comprehensive_scraping_job',
            'schedule': crontab(hour=5, minute=0, day_of_week=1),  # Monday 5 AM
            'options': {'queue': 'scraping'}
        }
    }
)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 300})
def scrape_source(self, source_name: str, max_events: int = None) -> Dict[str, Any]:
    """Scrape events from a specific source."""
    try:
        logger.info("Starting source scraping task", source=source_name, task_id=self.request.id)
        
        # Run async scraping in event loop
        result = asyncio.run(_scrape_source_async(source_name, max_events))
        
        logger.info(
            "Source scraping completed",
            source=source_name,
            task_id=self.request.id,
            success=result['success'],
            events_found=result.get('events_found', 0),
            events_saved=result.get('events_saved', 0)
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Source scraping failed",
            source=source_name,
            task_id=self.request.id,
            error=str(e),
            exc_info=True
        )
        
        # Retry with exponential backoff
        raise self.retry(countdown=300 * (2 ** self.request.retries), exc=e)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 600})
def daily_scraping_job(self) -> Dict[str, Any]:
    """Daily scraping job that processes all sources."""
    try:
        logger.info("Starting daily scraping job", task_id=self.request.id)
        
        result = asyncio.run(_daily_scraping_async())
        
        logger.info(
            "Daily scraping job completed",
            task_id=self.request.id,
            total_events_found=result.get('total_events_found', 0),
            total_events_saved=result.get('total_events_saved', 0),
            sources_processed=len(result.get('source_results', {})),
            errors=len(result.get('errors', []))
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Daily scraping job failed",
            task_id=self.request.id,
            error=str(e),
            exc_info=True
        )
        
        raise self.retry(countdown=600 * (2 ** self.request.retries), exc=e)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 900})
def comprehensive_scraping_job(self) -> Dict[str, Any]:
    """Weekly comprehensive scraping job with higher limits."""
    try:
        logger.info("Starting comprehensive scraping job", task_id=self.request.id)
        
        result = asyncio.run(_comprehensive_scraping_async())
        
        logger.info(
            "Comprehensive scraping job completed",
            task_id=self.request.id,
            total_events_found=result.get('total_events_found', 0),
            total_events_saved=result.get('total_events_saved', 0),
            sources_processed=len(result.get('source_results', {}))
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Comprehensive scraping job failed",
            task_id=self.request.id,
            error=str(e),
            exc_info=True
        )
        
        raise self.retry(countdown=900 * (2 ** self.request.retries), exc=e)


@celery_app.task(bind=True)
def cleanup_old_events(self) -> Dict[str, Any]:
    """Clean up old scraped events and maintain database."""
    try:
        logger.info("Starting cleanup task", task_id=self.request.id)
        
        result = asyncio.run(_cleanup_old_events_async())
        
        logger.info(
            "Cleanup task completed",
            task_id=self.request.id,
            events_removed=result.get('events_removed', 0),
            events_archived=result.get('events_archived', 0)
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Cleanup task failed",
            task_id=self.request.id,
            error=str(e),
            exc_info=True
        )
        
        return {'success': False, 'error': str(e)}


async def _scrape_source_async(source_name: str, max_events: int = None) -> Dict[str, Any]:
    """Async function to scrape a specific source."""
    scrapers = {
        'visitsingapore': VisitSingaporeScraper,
        'eventbrite': EventbriteScraper,
        'marinabaysands': MarinaBayScandsScraper,
        'sunteccity': SuntecCityScraper,
        'community_centers': CommunityCentersScraper,
    }
    
    scraper_class = scrapers.get(source_name)
    if not scraper_class:
        raise ValueError(f"Unknown source: {source_name}")
    
    processor = EventDataProcessor()
    
    try:
        # Initialize scraper with custom max_events if provided
        scraper_kwargs = {}
        if max_events:
            scraper_kwargs['max_events'] = max_events
            
        async with scraper_class(**scraper_kwargs) as scraper:
            # Scrape events
            events = await scraper.scrape_events()
            
            # Process and save events
            result = await processor.process_scraped_events(events, source_name)
            
            return {
                'success': result.success,
                'source': source_name,
                'events_found': result.events_found,
                'events_saved': result.events_saved,
                'errors': result.errors,
                'duration_seconds': result.duration_seconds,
                'start_time': result.start_time.isoformat(),
                'end_time': result.end_time.isoformat()
            }
            
    except Exception as e:
        logger.error("Error in source scraping", source=source_name, error=str(e))
        return {
            'success': False,
            'source': source_name,
            'events_found': 0,
            'events_saved': 0,
            'errors': [str(e)],
            'duration_seconds': 0,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': datetime.utcnow().isoformat()
        }


async def _daily_scraping_async() -> Dict[str, Any]:
    """Async function for daily scraping of all sources."""
    start_time = datetime.utcnow()
    source_results = {}
    errors = []
    total_events_found = 0
    total_events_saved = 0
    
    # Define sources with their daily limits
    sources = {
        'visitsingapore': 50,
        'eventbrite': 100,
        'marinabaysands': 30,
        'sunteccity': 20,
        'community_centers': 80,
    }
    
    # Process sources concurrently but with limited concurrency
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent scrapers
    
    async def scrape_with_semaphore(source_name: str, max_events: int):
        async with semaphore:
            return await _scrape_source_async(source_name, max_events)
    
    # Create tasks for all sources
    tasks = [
        scrape_with_semaphore(source_name, max_events)
        for source_name, max_events in sources.items()
    ]
    
    # Execute all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for source_name, result in zip(sources.keys(), results):
        if isinstance(result, Exception):
            error_msg = f"Error scraping {source_name}: {str(result)}"
            errors.append(error_msg)
            logger.error("Source scraping error", source=source_name, error=str(result))
        else:
            source_results[source_name] = result
            total_events_found += result.get('events_found', 0)
            total_events_saved += result.get('events_saved', 0)
    
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    return {
        'success': len(errors) == 0,
        'total_events_found': total_events_found,
        'total_events_saved': total_events_saved,
        'source_results': source_results,
        'errors': errors,
        'duration_seconds': duration,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'sources_processed': len([r for r in results if not isinstance(r, Exception)])
    }


async def _comprehensive_scraping_async() -> Dict[str, Any]:
    """Async function for comprehensive weekly scraping."""
    start_time = datetime.utcnow()
    source_results = {}
    errors = []
    total_events_found = 0
    total_events_saved = 0
    
    # Higher limits for comprehensive scraping
    sources = {
        'visitsingapore': 200,
        'eventbrite': 300,
        'marinabaysands': 100,
        'sunteccity': 80,
        'community_centers': 200,
    }
    
    # Process sources sequentially for comprehensive scraping to avoid overloading
    for source_name, max_events in sources.items():
        try:
            logger.info("Comprehensive scraping source", source=source_name, max_events=max_events)
            
            result = await _scrape_source_async(source_name, max_events)
            source_results[source_name] = result
            total_events_found += result.get('events_found', 0)
            total_events_saved += result.get('events_saved', 0)
            
            # Add delay between sources
            await asyncio.sleep(30)
            
        except Exception as e:
            error_msg = f"Error in comprehensive scraping {source_name}: {str(e)}"
            errors.append(error_msg)
            logger.error("Comprehensive scraping error", source=source_name, error=str(e))
    
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    return {
        'success': len(errors) == 0,
        'total_events_found': total_events_found,
        'total_events_saved': total_events_saved,
        'source_results': source_results,
        'errors': errors,
        'duration_seconds': duration,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'sources_processed': len([s for s in sources.keys() if s in source_results])
    }


async def _cleanup_old_events_async() -> Dict[str, Any]:
    """Async function to clean up old events."""
    from sqlalchemy import delete, update
    from app.models.event import Event
    from app.db.database import AsyncSessionLocal
    
    events_removed = 0
    events_archived = 0
    
    async with AsyncSessionLocal() as db:
        try:
            # Remove scraped events older than 30 days that are not approved
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Delete old unapproved scraped events
            delete_query = delete(Event).where(
                Event.source == 'scraped',
                Event.is_approved == False,
                Event.created_at < cutoff_date
            )
            
            result = await db.execute(delete_query)
            events_removed = result.rowcount
            
            # Archive old approved events (mark as inactive instead of deleting)
            archive_cutoff = datetime.utcnow() - timedelta(days=365)  # 1 year
            
            archive_query = update(Event).where(
                Event.date < archive_cutoff.date(),
                Event.is_active == True
            ).values(is_active=False)
            
            result = await db.execute(archive_query)
            events_archived = result.rowcount
            
            await db.commit()
            
            logger.info(
                "Cleanup completed",
                events_removed=events_removed,
                events_archived=events_archived
            )
            
        except Exception as e:
            await db.rollback()
            logger.error("Error in cleanup", error=str(e))
            raise
    
    return {
        'success': True,
        'events_removed': events_removed,
        'events_archived': events_archived
    }


# Task monitoring functions
@celery_app.task
def get_scraping_status() -> Dict[str, Any]:
    """Get current status of scraping tasks."""
    try:
        # Get active tasks
        active_tasks = celery_app.control.inspect().active()
        
        # Get scheduled tasks
        scheduled_tasks = celery_app.control.inspect().scheduled()
        
        # Get reserved tasks
        reserved_tasks = celery_app.control.inspect().reserved()
        
        return {
            'active_tasks': active_tasks,
            'scheduled_tasks': scheduled_tasks,
            'reserved_tasks': reserved_tasks,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting scraping status", error=str(e))
        return {'error': str(e)}


@celery_app.task
def health_check() -> Dict[str, Any]:
    """Health check task for monitoring."""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'timezone': 'Asia/Singapore'
    }