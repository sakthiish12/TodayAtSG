"""
Comprehensive data processing pipeline for scraped events.

This module provides advanced data validation, duplicate detection, geolocation
processing, and data enrichment specifically for Singapore events.
"""

import asyncio
import structlog
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import re
import hashlib
from difflib import SequenceMatcher
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from .base import ScrapedEvent, ScrapingResult
from app.core.config import settings
from app.models.event import Event
from app.models.category import Category
from app.models.tag import Tag
from app.db.database import AsyncSessionLocal
from app.utils.geolocation import geocode_address, is_in_singapore

logger = structlog.get_logger("data_processor")


class EventValidationError(Exception):
    """Exception raised when event validation fails."""
    pass


class EventDataProcessor:
    """Comprehensive event data processor with validation and enrichment."""
    
    def __init__(self):
        self.logger = structlog.get_logger("event_processor")
        self.seen_hashes: Set[str] = set()
        self.singapore_areas = self._load_singapore_areas()
        
    def _load_singapore_areas(self) -> Dict[str, Dict[str, Any]]:
        """Load Singapore area mappings for location validation."""
        return {
            # Central Region
            'orchard': {'region': 'Central', 'postal_codes': [238, 239]},
            'marina bay': {'region': 'Central', 'postal_codes': [018, 019]},
            'raffles place': {'region': 'Central', 'postal_codes': [048, 049]},
            'chinatown': {'region': 'Central', 'postal_codes': [058, 059]},
            'little india': {'region': 'Central', 'postal_codes': [207, 208]},
            'clarke quay': {'region': 'Central', 'postal_codes': [179]},
            'dhoby ghaut': {'region': 'Central', 'postal_codes': [189]},
            'city hall': {'region': 'Central', 'postal_codes': [179, 180]},
            
            # East Region
            'bedok': {'region': 'East', 'postal_codes': [460, 461, 462, 463, 464, 465, 466, 467, 468, 469]},
            'tampines': {'region': 'East', 'postal_codes': [520, 521, 522, 523, 524, 525, 526, 527, 528, 529]},
            'pasir ris': {'region': 'East', 'postal_codes': [510, 511, 512, 513, 514, 515, 516, 517, 518, 519]},
            'changi': {'region': 'East', 'postal_codes': [498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509]},
            
            # North Region
            'woodlands': {'region': 'North', 'postal_codes': [730, 731, 732, 733, 734, 735, 736, 737, 738, 739]},
            'yishun': {'region': 'North', 'postal_codes': [760, 761, 762, 763, 764, 765, 766, 767, 768, 769]},
            'sembawang': {'region': 'North', 'postal_codes': [750, 751, 752, 753, 754, 755, 756, 757, 758, 759]},
            
            # West Region
            'jurong west': {'region': 'West', 'postal_codes': [640, 641, 642, 643, 644, 645, 646, 647, 648, 649]},
            'clementi': {'region': 'West', 'postal_codes': [120, 121, 122, 123, 124, 125, 126, 127, 128, 129]},
            'bukit batok': {'region': 'West', 'postal_codes': [650, 651, 652, 653, 654, 655, 656, 657, 658, 659]},
            
            # Others
            'sentosa': {'region': 'South', 'postal_codes': [099]},
            'harbourfront': {'region': 'South', 'postal_codes': [109, 110, 111]},
        }
    
    async def process_scraped_events(self, events: List[ScrapedEvent], source: str) -> ScrapingResult:
        """Process a list of scraped events with comprehensive validation and enrichment."""
        start_time = datetime.utcnow()
        processed_events = []
        errors = []
        
        try:
            self.logger.info("Starting event processing", source=source, event_count=len(events))
            
            # Process events in batches for better performance
            batch_size = settings.SCRAPING_BATCH_SIZE
            for i in range(0, len(events), batch_size):
                batch = events[i:i + batch_size]
                batch_results = await asyncio.gather(
                    *[self._process_single_event(event, source) for event in batch],
                    return_exceptions=True
                )
                
                for event, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        errors.append(f"Error processing {event.title}: {str(result)}")
                        self.logger.warning("Event processing error", event_title=event.title, error=str(result))
                    elif result:
                        processed_events.append(result)
            
            # Save processed events to database
            events_saved = await self._save_events_to_database(processed_events, source)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            result = ScrapingResult(
                source=source,
                success=True,
                events_found=len(events),
                events_saved=events_saved,
                errors=errors,
                duration_seconds=duration,
                start_time=start_time,
                end_time=end_time,
                events=processed_events
            )
            
            self.logger.info(
                "Event processing completed",
                source=source,
                events_found=len(events),
                events_processed=len(processed_events),
                events_saved=events_saved,
                errors=len(errors),
                duration=duration
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Event processing failed", source=source, error=str(e), exc_info=True)
            
            return ScrapingResult(
                source=source,
                success=False,
                events_found=len(events),
                events_saved=0,
                errors=[str(e)],
                duration_seconds=(datetime.utcnow() - start_time).total_seconds(),
                start_time=start_time,
                end_time=datetime.utcnow(),
                events=[]
            )
    
    async def _process_single_event(self, event: ScrapedEvent, source: str) -> Optional[ScrapedEvent]:
        """Process a single event with validation and enrichment."""
        try:
            # Validate basic event data
            if not self._validate_event_data(event):
                return None
            
            # Check for duplicates
            if await self._is_duplicate_event(event):
                self.logger.debug("Duplicate event detected", title=event.title, source=source)
                return None
            
            # Enrich event data
            enriched_event = await self._enrich_event_data(event)
            
            # Validate enriched event
            if not self._validate_enriched_event(enriched_event):
                return None
            
            return enriched_event
            
        except Exception as e:
            self.logger.error("Error processing single event", event_title=event.title, error=str(e))
            return None
    
    def _validate_event_data(self, event: ScrapedEvent) -> bool:
        """Validate basic event data requirements."""
        try:
            # Title validation
            if not event.title or len(event.title.strip()) < 3:
                self.logger.debug("Invalid title", title=event.title)
                return False
            
            if len(event.title) > 255:
                event.title = event.title[:252] + "..."
            
            # Date validation
            if event.date:
                # Don't accept events too far in the past (more than 1 day)
                cutoff_date = date.today() - timedelta(days=1)
                if event.date < cutoff_date:
                    self.logger.debug("Event date too old", date=event.date, title=event.title)
                    return False
                
                # Don't accept events too far in the future (more than 2 years)
                future_cutoff = date.today() + timedelta(days=730)
                if event.date > future_cutoff:
                    self.logger.debug("Event date too far in future", date=event.date, title=event.title)
                    return False
            
            # Location validation for Singapore
            if not self._is_singapore_location(event.location, event.address):
                self.logger.debug("Non-Singapore location", location=event.location, address=event.address)
                return False
            
            # Content validation
            if event.description and len(event.description) > 2000:
                event.description = event.description[:1997] + "..."
            
            if event.short_description and len(event.short_description) > 500:
                event.short_description = event.short_description[:497] + "..."
            
            return True
            
        except Exception as e:
            self.logger.error("Error validating event data", error=str(e))
            return False
    
    def _is_singapore_location(self, location: str, address: str) -> bool:
        """Check if the location is in Singapore."""
        location_text = f"{location} {address}".lower()
        
        # Check for Singapore indicators
        singapore_indicators = [
            'singapore', 'sg', 'raffles', 'orchard', 'marina bay', 'sentosa',
            'jurong', 'tampines', 'woodlands', 'yishun', 'bedok', 'clementi',
            'bukit', 'toa payoh', 'ang mo kio', 'hougang', 'sengkang',
            'pasir ris', 'changi', 'harbourfront', 'dhoby ghaut', 'bugis',
            'chinatown', 'little india', 'clarke quay'
        ]
        
        return any(indicator in location_text for indicator in singapore_indicators)
    
    async def _is_duplicate_event(self, event: ScrapedEvent) -> bool:
        """Check if event is a duplicate using various similarity metrics."""
        try:
            # Generate hash for quick lookup
            event_hash = event.generate_hash()
            
            if event_hash in self.seen_hashes:
                return True
            
            # Check database for similar events
            async with AsyncSessionLocal() as db:
                # Look for events with similar title and date
                similarity_query = select(Event).where(
                    and_(
                        Event.date == event.date,
                        func.lower(Event.title).contains(event.title.lower()[:20])
                    )
                )
                
                result = await db.execute(similarity_query)
                similar_events = result.scalars().all()
                
                # Check title similarity
                for existing_event in similar_events:
                    similarity = SequenceMatcher(None, event.title.lower(), existing_event.title.lower()).ratio()
                    if similarity > 0.8:  # 80% similarity threshold
                        self.logger.debug(
                            "Similar event found",
                            new_title=event.title,
                            existing_title=existing_event.title,
                            similarity=similarity
                        )
                        return True
            
            # Add to seen hashes
            self.seen_hashes.add(event_hash)
            return False
            
        except Exception as e:
            self.logger.error("Error checking duplicate event", error=str(e))
            return False
    
    async def _enrich_event_data(self, event: ScrapedEvent) -> ScrapedEvent:
        """Enrich event data with additional information."""
        try:
            # Geocoding if coordinates not available
            if not event.latitude or not event.longitude:
                if event.address:
                    coordinates = await self._geocode_address(event.address)
                    if coordinates:
                        event.latitude = coordinates[0]
                        event.longitude = coordinates[1]
                        self.logger.debug("Geocoded address", address=event.address, lat=event.latitude, lng=event.longitude)
            
            # Enhance location information
            event = self._enhance_location_info(event)
            
            # Validate and enhance category
            event.category_slug = self._validate_category(event.category_slug)
            
            # Enhance tags
            event.tag_slugs = self._enhance_tags(event)
            
            # Set default time if missing
            if not event.time:
                event.time = self._infer_default_time(event)
            
            # Generate external ID if missing
            if not event.external_id:
                event.external_id = self._generate_external_id(event)
            
            return event
            
        except Exception as e:
            self.logger.error("Error enriching event data", error=str(e))
            return event
    
    async def _geocode_address(self, address: str) -> Optional[Tuple[Decimal, Decimal]]:
        """Geocode Singapore address to coordinates."""
        try:
            # Use the geolocation service
            coordinates = await geocode_address(address)
            if coordinates and is_in_singapore(coordinates[0], coordinates[1]):
                return Decimal(str(coordinates[0])), Decimal(str(coordinates[1]))
        except Exception as e:
            self.logger.debug("Geocoding failed", address=address, error=str(e))
        
        return None
    
    def _enhance_location_info(self, event: ScrapedEvent) -> ScrapedEvent:
        """Enhance location information with Singapore-specific data."""
        location_lower = event.location.lower()
        address_lower = event.address.lower()
        
        # Identify Singapore area
        for area, info in self.singapore_areas.items():
            if area in location_lower or area in address_lower:
                if not event.venue or len(event.venue) < len(event.location):
                    event.venue = event.location
                event.location = f"{area.title()}, Singapore"
                break
        
        # Ensure location ends with Singapore
        if 'singapore' not in event.location.lower():
            if event.location and event.location != 'Singapore':
                event.location = f"{event.location}, Singapore"
            else:
                event.location = "Singapore"
        
        return event
    
    def _validate_category(self, category_slug: str) -> str:
        """Validate and normalize category slug."""
        valid_categories = [
            'concerts', 'sports', 'festivals', 'exhibitions', 'workshops',
            'family', 'food', 'nightlife', 'theatre', 'business', 'general'
        ]
        
        if category_slug in valid_categories:
            return category_slug
        
        # Try to map similar categories
        category_mappings = {
            'music': 'concerts',
            'art': 'exhibitions',
            'arts': 'exhibitions',
            'dining': 'food',
            'entertainment': 'general',
            'shopping': 'general',
            'fitness': 'sports',
            'health': 'workshops',
            'education': 'workshops',
            'networking': 'business',
            'conference': 'business',
        }
        
        return category_mappings.get(category_slug, 'general')
    
    def _enhance_tags(self, event: ScrapedEvent) -> List[str]:
        """Enhance event tags with additional relevant tags."""
        tags = set(event.tag_slugs) if event.tag_slugs else set()
        
        content = f"{event.title} {event.description} {event.venue}".lower()
        
        # Time-based tags
        if event.time:
            hour = event.time.hour
            if 6 <= hour < 12:
                tags.add('morning')
            elif 12 <= hour < 17:
                tags.add('afternoon')
            elif 17 <= hour < 21:
                tags.add('evening')
            elif 21 <= hour or hour < 6:
                tags.add('night')
        
        # Date-based tags
        if event.date:
            if event.date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                tags.add('weekend')
            else:
                tags.add('weekday')
        
        # Price-based tags
        if event.price_info:
            price_lower = event.price_info.lower()
            if any(word in price_lower for word in ['free', 'complimentary', 'no charge']):
                tags.add('free')
            elif any(word in price_lower for word in ['premium', 'vip', 'exclusive']):
                tags.add('premium')
        
        # Venue-specific tags
        venue_lower = event.venue.lower()
        if any(word in venue_lower for word in ['mall', 'shopping']):
            tags.add('shopping-mall')
        elif any(word in venue_lower for word in ['hotel', 'resort']):
            tags.add('hotel')
        elif any(word in venue_lower for word in ['community', 'cc']):
            tags.add('community-center')
        
        # Remove duplicates and invalid tags
        valid_tags = [tag for tag in tags if tag and len(tag) <= 50 and re.match(r'^[a-z0-9-]+$', tag)]
        
        return valid_tags[:10]  # Limit to 10 tags
    
    def _infer_default_time(self, event: ScrapedEvent) -> time:
        """Infer default time based on event characteristics."""
        category_defaults = {
            'concerts': time(20, 0),      # 8 PM
            'nightlife': time(22, 0),     # 10 PM
            'theatre': time(20, 0),       # 8 PM
            'business': time(9, 0),       # 9 AM
            'workshops': time(14, 0),     # 2 PM
            'family': time(10, 0),        # 10 AM
            'sports': time(18, 0),        # 6 PM
            'food': time(19, 0),          # 7 PM
        }
        
        return category_defaults.get(event.category_slug, time(19, 0))  # Default 7 PM
    
    def _generate_external_id(self, event: ScrapedEvent) -> str:
        """Generate external ID for the event."""
        content = f"{event.source}|{event.title}|{event.date or 'no-date'}|{event.venue}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _validate_enriched_event(self, event: ScrapedEvent) -> bool:
        """Final validation of enriched event data."""
        try:
            # Ensure required fields are present
            if not event.title or not event.category_slug:
                return False
            
            # Validate coordinates if present
            if event.latitude and event.longitude:
                lat_float = float(event.latitude)
                lng_float = float(event.longitude)
                
                # Singapore bounds approximately
                if not (1.0 <= lat_float <= 1.5 and 103.5 <= lng_float <= 104.5):
                    self.logger.debug("Coordinates outside Singapore", lat=lat_float, lng=lng_float, title=event.title)
                    event.latitude = None
                    event.longitude = None
            
            return True
            
        except Exception as e:
            self.logger.error("Error validating enriched event", error=str(e))
            return False
    
    async def _save_events_to_database(self, events: List[ScrapedEvent], source: str) -> int:
        """Save processed events to database."""
        saved_count = 0
        
        async with AsyncSessionLocal() as db:
            try:
                # Get categories and tags for lookups
                categories_result = await db.execute(select(Category))
                categories = {cat.slug: cat for cat in categories_result.scalars().all()}
                
                tags_result = await db.execute(select(Tag))
                tags = {tag.slug: tag for tag in tags_result.scalars().all()}
                
                for event_data in events:
                    try:
                        # Get category
                        category = categories.get(event_data.category_slug)
                        if not category:
                            self.logger.warning("Category not found", category_slug=event_data.category_slug)
                            continue
                        
                        # Create event
                        event = Event(
                            title=event_data.title,
                            description=event_data.description,
                            short_description=event_data.short_description,
                            date=event_data.date,
                            time=event_data.time,
                            end_date=event_data.end_date,
                            end_time=event_data.end_time,
                            location=event_data.location,
                            venue=event_data.venue,
                            address=event_data.address,
                            latitude=event_data.latitude,
                            longitude=event_data.longitude,
                            age_restrictions=event_data.age_restrictions,
                            price_info=event_data.price_info,
                            external_url=event_data.external_url,
                            image_url=event_data.image_url,
                            category_id=category.id,
                            source='scraped',
                            scraped_from=event_data.scraped_from,
                            external_id=event_data.external_id,
                            last_scraped=datetime.utcnow(),
                            is_approved=False,  # Scraped events need approval
                            is_active=True,
                        )
                        
                        db.add(event)
                        await db.flush()  # Get event ID
                        
                        # Add tags
                        for tag_slug in event_data.tag_slugs:
                            tag = tags.get(tag_slug)
                            if tag:
                                event.tags.append(tag)
                        
                        saved_count += 1
                        
                    except Exception as e:
                        self.logger.error(
                            "Error saving event",
                            event_title=event_data.title,
                            error=str(e)
                        )
                        continue
                
                await db.commit()
                
                self.logger.info("Events saved to database", saved_count=saved_count, source=source)
                
            except Exception as e:
                await db.rollback()
                self.logger.error("Error saving events to database", error=str(e), exc_info=True)
                raise
        
        return saved_count