"""
Enhanced web scraping service for collecting events from various Singapore sources.

This module provides:
- Multi-source web scrapers with extensible framework
- Data processing pipeline with validation and duplicate detection
- Background task integration with Celery
- Rate limiting and ethical scraping practices
- Geolocation processing and data enrichment
- Comprehensive error handling and monitoring
"""

import asyncio
import structlog
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, date, time, timedelta
import pytz

from app.core.config import settings
from app.services.scrapers.base import ScrapingResult
from app.services.scrapers.visitsingapore import VisitSingaporeScraper
from app.services.scrapers.eventbrite import EventbriteScraper  
from app.services.scrapers.marinabaysands import MarinaBayScandsScraper
from app.services.scrapers.sunteccity import SuntecCityScraper
from app.services.scrapers.community_centers import CommunityCentersScraper
from app.services.scrapers.data_processor import EventDataProcessor

logger = structlog.get_logger("scraping")
singapore_tz = pytz.timezone('Asia/Singapore')


class EventScrapingService:
    """Enhanced service for coordinating event scraping from multiple sources."""
    
    def __init__(self):
        self.logger = structlog.get_logger("scraping_service")
        self.data_processor = EventDataProcessor()
        self.scrapers = {
            "visitsingapore": VisitSingaporeScraper,
            "eventbrite": EventbriteScraper,
            "marinabaysands": MarinaBayScandsScraper,
            "sunteccity": SuntecCityScraper,
            "community_centers": CommunityCentersScraper,
        }
    
    async def scrape_all_sources(self) -> Dict[str, ScrapingResult]:
        """Scrape events from all configured sources with enhanced processing."""
        results = {}
        
        # Process sources with controlled concurrency
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent scrapers
        
        async def scrape_source_with_semaphore(source_name: str, scraper_class):
            async with semaphore:
                return await self._scrape_single_source(source_name, scraper_class)
        
        # Create tasks for all sources
        tasks = [
            scrape_source_with_semaphore(source_name, scraper_class)
            for source_name, scraper_class in self.scrapers.items()
        ]
        
        # Execute all tasks
        scraping_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for source_name, result in zip(self.scrapers.keys(), scraping_results):
            if isinstance(result, Exception):
                self.logger.error("Source scraping error", source=source_name, error=str(result))
                results[source_name] = ScrapingResult(
                    source=source_name,
                    success=False,
                    events_found=0,
                    events_saved=0,
                    errors=[str(result)],
                    duration_seconds=0,
                    start_time=datetime.utcnow(),
                    end_time=datetime.utcnow()
                )
            else:
                results[source_name] = result
        
        total_events_found = sum(r.events_found for r in results.values())
        total_events_saved = sum(r.events_saved for r in results.values())
        
        self.logger.info(
            "All sources scraped",
            total_events_found=total_events_found,
            total_events_saved=total_events_saved,
            successful_sources=len([r for r in results.values() if r.success])
        )
        
        return results
    
    async def _scrape_single_source(self, source_name: str, scraper_class) -> ScrapingResult:
        """Scrape a single source with comprehensive processing."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Starting source scraping", source=source_name)
            
            # Initialize scraper
            async with scraper_class() as scraper:
                # Scrape raw events
                scraped_events = await scraper.scrape_events()
                
                self.logger.info(
                    "Raw scraping completed",
                    source=source_name,
                    events_scraped=len(scraped_events)
                )
                
                # Process events through data pipeline
                result = await self.data_processor.process_scraped_events(
                    scraped_events, source_name
                )
                
                return result
                
        except Exception as e:
            self.logger.error(
                "Source scraping failed",
                source=source_name,
                error=str(e),
                exc_info=True
            )
            
            return ScrapingResult(
                source=source_name,
                success=False,
                events_found=0,
                events_saved=0,
                errors=[str(e)],
                duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.utcnow()
            )
    
    async def scrape_source(self, source_name: str, max_events: int = None) -> ScrapingResult:
        """Scrape events from a specific source."""
        scraper_class = self.scrapers.get(source_name)
        if not scraper_class:
            raise ValueError(f"Unknown source: {source_name}")
        
        # Override max_events if specified
        if max_events:
            # Create scraper instance with custom max_events
            scraper_instance = scraper_class()
            scraper_instance.max_events = max_events
            
            start_time = datetime.utcnow()
            try:
                async with scraper_instance:
                    scraped_events = await scraper_instance.scrape_events()
                    result = await self.data_processor.process_scraped_events(
                        scraped_events, source_name
                    )
                    return result
            except Exception as e:
                return ScrapingResult(
                    source=source_name,
                    success=False,
                    events_found=0,
                    events_saved=0,
                    errors=[str(e)],
                    duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
                    start_time=start_time,
                    end_time=datetime.utcnow()
                )
        else:
            return await self._scrape_single_source(source_name, scraper_class)
    
    async def run_daily_scraping(self) -> Dict[str, Any]:
        """Run the daily scraping job with enhanced processing."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Starting daily scraping job")
            
            # Scrape all sources with processing
            scraping_results = await self.scrape_all_sources()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Aggregate results
            total_events_found = sum(r.events_found for r in scraping_results.values())
            total_events_saved = sum(r.events_saved for r in scraping_results.values())
            successful_sources = [name for name, result in scraping_results.items() if result.success]
            failed_sources = [name for name, result in scraping_results.items() if not result.success]
            all_errors = []
            
            for result in scraping_results.values():
                all_errors.extend(result.errors)
            
            result = {
                "status": "success" if len(successful_sources) > 0 else "error",
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "sources_scraped": successful_sources,
                "sources_failed": failed_sources,
                "total_events_found": total_events_found,
                "total_events_saved": total_events_saved,
                "source_results": {
                    name: {
                        "success": result.success,
                        "events_found": result.events_found,
                        "events_saved": result.events_saved,
                        "errors": result.errors,
                        "duration_seconds": result.duration_seconds
                    }
                    for name, result in scraping_results.items()
                },
                "errors": all_errors,
            }
            
            self.logger.info(
                "Daily scraping completed",
                duration=duration,
                events_saved=total_events_saved,
                total_found=total_events_found,
                successful_sources=len(successful_sources),
                failed_sources=len(failed_sources)
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Daily scraping failed", error=str(e), exc_info=True)
            
            return {
                "status": "error",
                "start_time": start_time,
                "end_time": datetime.utcnow(),
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "error": str(e),
                "sources_scraped": [],
                "sources_failed": list(self.scrapers.keys()),
                "total_events_found": 0,
                "total_events_saved": 0,
            }
    
    def get_scraper_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available scrapers."""
        scraper_info = {}
        
        for source_name, scraper_class in self.scrapers.items():
            # Create temporary instance to get info
            scraper = scraper_class()
            scraper_info[source_name] = {
                "name": scraper.name,
                "base_url": scraper.base_url,
                "max_events": scraper.max_events,
                "description": scraper.__class__.__doc__ or "No description available"
            }
        
        return scraper_info
    
    async def test_scraper(self, source_name: str, limit: int = 5) -> Dict[str, Any]:
        """Test a specific scraper with a small number of events."""
        try:
            result = await self.scrape_source(source_name, max_events=limit)
            
            return {
                "success": result.success,
                "source": source_name,
                "events_found": result.events_found,
                "events_processed": len(result.events) if result.events else 0,
                "errors": result.errors,
                "duration_seconds": result.duration_seconds,
                "sample_events": [
                    {
                        "title": event.title,
                        "date": event.date.isoformat() if event.date else None,
                        "location": event.location,
                        "category": event.category_slug,
                        "tags": event.tag_slugs
                    }
                    for event in (result.events[:3] if result.events else [])
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "source": source_name,
                "error": str(e),
                "events_found": 0,
                "events_processed": 0
            }


# Create global scraping service instance
scraping_service = EventScrapingService()