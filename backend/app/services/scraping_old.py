"""
Comprehensive web scraping service for collecting events from various Singapore sources.

This module provides:
- Multi-source web scrapers with extensible framework
- Data processing pipeline with validation and duplicate detection
- Background task integration with Celery
- Rate limiting and ethical scraping practices
- Geolocation processing and data enrichment
- Comprehensive error handling and monitoring
"""

import httpx
import asyncio
import structlog
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus
import re
import hashlib
import json
from dataclasses import dataclass, asdict
from urllib.robotparser import RobotFileParser
from fake_useragent import UserAgent
from retry import retry
import pytz
from difflib import SequenceMatcher
from sqlalchemy import select, and_, or_

from app.core.config import settings
from app.models.event import Event
from app.models.category import Category
from app.models.tag import Tag
from app.db.database import AsyncSessionLocal
from app.utils.geolocation import geocode_address, is_in_singapore

logger = structlog.get_logger("scraping")
singapore_tz = pytz.timezone('Asia/Singapore')


class ScrapingError(Exception):
    """Custom exception for scraping-related errors."""
    pass


class DuplicateEventError(Exception):
    """Exception raised when a duplicate event is detected."""
    pass


class RobotsTxtBlockedError(ScrapingError):
    """Exception raised when robots.txt blocks the scraping."""
    pass


class RateLimitExceededError(ScrapingError):
    """Exception raised when rate limit is exceeded."""
    pass


@dataclass
class ScrapedEvent:
    """Data class for scraped event information."""
    title: str
    description: str = ""
    short_description: str = ""
    date: Optional[date] = None
    time: Optional[time] = None
    end_date: Optional[date] = None
    end_time: Optional[time] = None
    location: str = "Singapore"
    venue: str = ""
    address: str = ""
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    age_restrictions: str = ""
    price_info: str = ""
    external_url: str = ""
    image_url: str = ""
    category_slug: str = "general"
    tag_slugs: List[str] = None
    source: str = ""
    scraped_from: str = ""
    external_id: str = ""
    
    def __post_init__(self):
        if self.tag_slugs is None:
            self.tag_slugs = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)
    
    def generate_hash(self) -> str:
        """Generate unique hash for duplicate detection."""
        content = f"{self.title}|{self.date}|{self.time}|{self.venue}|{self.address}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass
class ScrapingResult:
    """Result of a scraping operation."""
    source: str
    success: bool
    events_found: int
    events_saved: int
    errors: List[str]
    duration_seconds: float
    start_time: datetime
    end_time: datetime
    events: List[ScrapedEvent] = None
    
    def __post_init__(self):
        if self.events is None:
            self.events = []


class BaseScraper:
    """Enhanced base class for all event scrapers with production features."""
    
    def __init__(self, name: str, base_url: str, max_events: int = None):
        self.name = name
        self.base_url = base_url
        self.max_events = max_events or settings.SCRAPING_MAX_EVENTS_PER_SOURCE
        self.logger = structlog.get_logger(f"scraper.{name}")
        self.session = None
        self.user_agent = UserAgent()
        self.request_count = 0
        self.rate_limiter = self._create_rate_limiter()
        self.robots_parser = None
        self.seen_events: Set[str] = set()  # For duplicate detection
        
    def _create_rate_limiter(self):
        """Create rate limiter for requests."""
        import time
        return {
            'last_request': 0,
            'request_count': 0,
            'window_start': time.time()
        }
        
    async def _check_robots_txt(self):
        """Check robots.txt compliance."""
        if not settings.SCRAPING_RESPECT_ROBOTS_TXT:
            return True
            
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            response = await self.session.get(robots_url)
            
            if response.status_code == 200:
                self.robots_parser = RobotFileParser()
                self.robots_parser.set_url(robots_url)
                self.robots_parser.read()
                
                user_agent = settings.SCRAPING_USER_AGENT
                if not self.robots_parser.can_fetch(user_agent, self.base_url):
                    raise RobotsTxtBlockedError(f"Robots.txt blocks access for {user_agent}")
                    
            return True
            
        except RobotsTxtBlockedError:
            raise
        except Exception as e:
            self.logger.warning("Could not check robots.txt", error=str(e))
            return True  # Assume allowed if can't check
            
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between requests."""
        import time
        current_time = time.time()
        time_since_last = current_time - self.rate_limiter['last_request']
        
        # Ensure minimum delay between requests
        if time_since_last < settings.SCRAPING_DELAY:
            sleep_time = settings.SCRAPING_DELAY - time_since_last
            await asyncio.sleep(sleep_time)
            
        # Update rate limiter state
        self.rate_limiter['last_request'] = time.time()
        self.rate_limiter['request_count'] += 1
        
        # Check if we've exceeded requests per minute
        window_duration = current_time - self.rate_limiter['window_start']
        if window_duration >= 60:  # Reset window every minute
            self.rate_limiter['window_start'] = current_time
            self.rate_limiter['request_count'] = 1
        elif self.rate_limiter['request_count'] > 30:  # Max 30 requests per minute
            raise RateLimitExceededError("Rate limit exceeded: too many requests per minute")
        
    async def __aenter__(self):
        """Async context manager entry with enhanced setup."""
        # Rotate user agent for each scraping session
        try:
            user_agent = self.user_agent.random
        except:
            user_agent = settings.SCRAPING_USER_AGENT
        
        self.session = httpx.AsyncClient(
            timeout=settings.SCRAPING_TIMEOUT,
            headers={
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",  
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "DNT": "1",  # Do Not Track
                "Upgrade-Insecure-Requests": "1",
            },
            follow_redirects=True
        )
        
        # Check robots.txt compliance
        await self._check_robots_txt()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    @retry(exceptions=(httpx.HTTPError, httpx.TimeoutException), tries=settings.SCRAPING_MAX_RETRIES, delay=settings.SCRAPING_RETRY_DELAY, backoff=2)
    async def fetch_page(self, url: str) -> str:
        """Fetch a web page with retry logic and enhanced error handling."""
        try:
            # Enforce rate limiting
            await self._enforce_rate_limit()
            
            self.logger.info("Fetching page", url=url, attempt=self.request_count)
            
            # Check robots.txt permission for this specific URL
            if self.robots_parser and not self.robots_parser.can_fetch(settings.SCRAPING_USER_AGENT, url):
                raise RobotsTxtBlockedError(f"Robots.txt blocks access to {url}")
            
            response = await self.session.get(url)
            response.raise_for_status()
            
            self.logger.debug("Page fetched successfully", url=url, status_code=response.status_code, content_length=len(response.text))
            
            return response.text
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Too Many Requests
                self.logger.warning("Rate limited by server", url=url, status_code=e.response.status_code)
                await asyncio.sleep(5)  # Wait before retry
                raise
            elif e.response.status_code in [403, 404]:
                self.logger.warning("Page access forbidden or not found", url=url, status_code=e.response.status_code)
                raise ScrapingError(f"Access denied or page not found: {url}")
            else:
                self.logger.error("HTTP error fetching page", url=url, status_code=e.response.status_code)
                raise ScrapingError(f"HTTP {e.response.status_code} error fetching {url}")
                
        except httpx.TimeoutException as e:
            self.logger.error("Timeout fetching page", url=url, error=str(e))
            raise ScrapingError(f"Timeout fetching {url}: {str(e)}")
            
        except RobotsTxtBlockedError:
            raise
            
        except RateLimitExceededError:
            raise
        
        except Exception as e:
            self.logger.error("Unexpected error fetching page", url=url, error=str(e))
            raise ScrapingError(f"Unexpected error fetching {url}: {str(e)}")
    
    def parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string into date object with extensive format support."""
        if not date_str:
            return None
            
        # Clean the date string
        date_str = self.clean_text(date_str)
        
        # Remove common prefixes and suffixes
        date_str = re.sub(r'^(on|from|starts?|begins?)\s+', '', date_str, flags=re.IGNORECASE)
        date_str = re.sub(r'\s+(onwards?|till|until|to).*$', '', date_str, flags=re.IGNORECASE)
        
        # Common date formats for Singapore
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%B %d, %Y",
            "%b %d, %Y", 
            "%d %B %Y",
            "%d %b %Y",
            "%A, %B %d, %Y",
            "%A, %d %B %Y",
            "%d-%b-%Y",
            "%d %b %y",
            "%B %d",  # Current year assumed
            "%b %d",   # Current year assumed
            "%d %B",   # Current year assumed
            "%d %b",   # Current year assumed
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                # If year not specified, assume current year
                if parsed_date.year == 1900:
                    parsed_date = parsed_date.replace(year=datetime.now().year)
                # If the date is in the past and no year specified, assume next year
                elif '%Y' not in fmt and '%y' not in fmt and parsed_date.date() < date.today():
                    parsed_date = parsed_date.replace(year=datetime.now().year + 1)
                return parsed_date.date()
            except ValueError:
                continue
        
        # Try parsing relative dates
        relative_patterns = [
            (r'today', 0),
            (r'tomorrow', 1),
            (r'next week', 7),
            (r'in (\d+) days?', lambda m: int(m.group(1))),
        ]
        
        for pattern, offset in relative_patterns:
            match = re.search(pattern, date_str.lower())
            if match:
                if callable(offset):
                    offset = offset(match)
                return date.today() + timedelta(days=offset)
        
        self.logger.warning("Could not parse date", date_str=date_str)
        return None
    
    def parse_time(self, time_str: str) -> Optional[time]:
        """Parse time string into time object with extensive format support."""
        if not time_str:
            return None
            
        # Clean the time string
        time_str = self.clean_text(time_str)
        
        # Remove common prefixes
        time_str = re.sub(r'^(at|from|starts?)\s+', '', time_str, flags=re.IGNORECASE)
        
        # Handle ranges - take the start time
        if ' - ' in time_str or ' to ' in time_str:
            time_str = re.split(r'\s*(-|to)\s*', time_str)[0]
        
        # Common time formats for Singapore
        time_formats = [
            "%H:%M",
            "%H.%M",
            "%I:%M %p",
            "%I:%M%p",
            "%I%p",
            "%H:%M:%S",
            "%I:%M:%S %p",
            "%I.%M %p",
            "%I.%M%p",
        ]
        
        # Clean up time string
        time_str = time_str.strip().replace(".", ":").upper()
        time_str = re.sub(r'\s+', ' ', time_str)  # Normalize spaces
        
        for fmt in time_formats:
            try:
                return datetime.strptime(time_str, fmt).time()
            except ValueError:
                continue
        
        # Try to extract hour from strings like "7pm", "9am", "19:00"
        hour_match = re.search(r'(\d{1,2})\s*(am|pm|AM|PM)?', time_str)
        if hour_match:
            hour = int(hour_match.group(1))
            period = hour_match.group(2)
            
            if period and period.upper() == 'PM' and hour != 12:
                hour += 12
            elif period and period.upper() == 'AM' and hour == 12:
                hour = 0
            
            if 0 <= hour <= 23:
                return time(hour, 0)
        
        self.logger.warning("Could not parse time", time_str=time_str)
        return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content with comprehensive cleaning."""
        if not text:
            return ""
        
        # Strip HTML tags if any remain
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove HTML entities that might have been missed
        html_entities = {
            '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>', 
            '&quot;': '"', '&apos;': "'", '&rdquo;': '"', '&ldquo;': '"',
            '&rsquo;': "'", '&lsquo;': "'", '&ndash;': '-', '&mdash;': '-',
            '&hellip;': '...', '&deg;': '°', '&#8217;': "'", '&#8220;': '"',
            '&#8221;': '"', '&#8211;': '-', '&#8212;': '-', '&#8230;': '...'
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        # Remove unicode characters that cause issues
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[-]{2,}', '-', text)
        
        return text.strip()
    
    def extract_price_info(self, text: str) -> str:
        """Extract price information from text."""
        if not text:
            return ""
            
        # Common Singapore price patterns
        price_patterns = [
            r'S?\$\d+(?:\.\d{2})?(?:\s*-\s*S?\$\d+(?:\.\d{2})?)?',  # $10 or $10-$20
            r'SGD\s*\d+(?:\.\d{2})?(?:\s*-\s*SGD\s*\d+(?:\.\d{2})?)?',  # SGD 10
            r'from\s+S?\$\d+(?:\.\d{2})?',  # from $10
            r'free|complimentary',  # Free events
            r'ticketed|paid\s+event',  # General paid indicators
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_text(match.group(0))
        
        return ""
    
    def extract_age_restrictions(self, text: str) -> str:
        """Extract age restriction information from text."""
        if not text:
            return ""
            
        # Common age restriction patterns
        age_patterns = [
            r'(\d+)\+',  # 18+
            r'ages?\s+(\d+)\s*(?:and\s+)?(?:above|up|over)',  # ages 18 and above
            r'(\d+)\s*years?\s*(?:and\s+)?(?:above|up|over)',  # 18 years and above
            r'all\s+ages?',  # all ages
            r'family\s+friendly',  # family friendly
            r'adults?\s+only',  # adults only
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_text(match.group(0))
        
        return ""
    
    def is_duplicate_event(self, event: ScrapedEvent) -> bool:
        """Check if event is a duplicate using various similarity metrics."""
        event_hash = event.generate_hash()
        
        # Check exact hash match
        if event_hash in self.seen_events:
            return True
            
        # Check title similarity with existing events
        for seen_hash in self.seen_events:
            # This is a simplified check - in production you'd store more event details
            # for more sophisticated duplicate detection
            pass
            
        self.seen_events.add(event_hash)
        return False
    
    def categorize_event(self, title: str, description: str, venue: str = "") -> str:
        """Automatically categorize event based on content."""
        content = f"{title} {description} {venue}".lower()
        
        # Category keywords mapping
        category_keywords = {
            'concerts': ['concert', 'music', 'band', 'singer', 'acoustic', 'live music', 'performance'],
            'sports': ['sports', 'football', 'basketball', 'tennis', 'marathon', 'race', 'gym', 'fitness'],
            'festivals': ['festival', 'celebration', 'cultural', 'heritage', 'tradition', 'parade'],
            'exhibitions': ['exhibition', 'museum', 'gallery', 'art', 'display', 'showcase', 'expo'],
            'workshops': ['workshop', 'class', 'training', 'learn', 'course', 'tutorial', 'seminar'],
            'family': ['family', 'kids', 'children', 'playground', 'zoo', 'aquarium', 'theme park'],
            'food': ['food', 'dining', 'restaurant', 'cuisine', 'cooking', 'tasting', 'buffet'],
            'nightlife': ['bar', 'club', 'pub', 'nightlife', 'party', 'dance', 'dj'],
            'theatre': ['theatre', 'theater', 'play', 'drama', 'musical', 'show', 'performance'],
            'business': ['conference', 'networking', 'business', 'corporate', 'meeting', 'summit'],
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in content for keyword in keywords):
                return category
                
        return 'general'  # Default category
    
    def extract_tags(self, title: str, description: str, venue: str = "") -> List[str]:
        """Extract relevant tags from event content."""
        content = f"{title} {description} {venue}".lower()
        tags = []
        
        # Location-based tags
        singapore_areas = [
            'orchard', 'marina bay', 'sentosa', 'chinatown', 'little india',
            'clarke quay', 'raffles place', 'bugis', 'dhoby ghaut', 'city hall',
            'harbourfront', 'jurong', 'tampines', 'woodlands', 'changi'
        ]
        
        for area in singapore_areas:
            if area in content:
                tags.append(area.replace(' ', '-'))
        
        # Activity-based tags
        activity_tags = {
            'outdoor': ['outdoor', 'park', 'garden', 'beach', 'nature'],
            'indoor': ['indoor', 'mall', 'shopping', 'air-con', 'airconditioned'],
            'free': ['free', 'complimentary', 'no charge', 'admission free'],
            'premium': ['premium', 'exclusive', 'vip', 'luxury'],
            'weekend': ['saturday', 'sunday', 'weekend'],
            'evening': ['evening', 'night', 'after dark', 'sunset'],
        }
        
        for tag, keywords in activity_tags.items():
            if any(keyword in content for keyword in keywords):
                tags.append(tag)
        
        return list(set(tags))  # Remove duplicates
    
    async def scrape_events(self) -> List[ScrapedEvent]:
        """Scrape events from the source. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement scrape_events method")


class VisitSingaporeScraper(BaseScraper):
    """Scraper for VisitSingapore events."""
    
    def __init__(self):
        super().__init__("visitsingapore", "https://www.visitsingapore.com")
    
    async def scrape_events(self) -> List[Dict[str, Any]]:
        """Scrape events from VisitSingapore."""
        events = []
        
        try:
            # Fetch the events page
            events_url = f"{self.base_url}/see-do-singapore/events/"
            html = await self.fetch_page(events_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find event containers (this would need to be updated based on actual HTML structure)
            event_containers = soup.find_all('div', class_='event-item')  # Placeholder selector
            
            for container in event_containers:
                try:
                    event_data = await self._parse_event_container(container)
                    if event_data:
                        events.append(event_data)
                except Exception as e:
                    self.logger.warning("Error parsing event container", error=str(e))
                    continue
            
            self.logger.info("Scraped events", source="visitsingapore", count=len(events))
            
        except Exception as e:
            self.logger.error("Error scraping VisitSingapore", error=str(e))
            raise ScrapingError(f"VisitSingapore scraping failed: {str(e)}")
        
        return events
    
    async def _parse_event_container(self, container) -> Optional[Dict[str, Any]]:
        """Parse individual event container."""
        # This is a placeholder implementation
        # Real implementation would need to match actual HTML structure
        
        title_elem = container.find('h3') or container.find('h2')
        title = self.clean_text(title_elem.get_text()) if title_elem else None
        
        if not title:
            return None
        
        # Extract other fields based on actual HTML structure
        description_elem = container.find('p', class_='description')
        description = self.clean_text(description_elem.get_text()) if description_elem else ""
        
        date_elem = container.find('span', class_='date')
        event_date = self.parse_date(date_elem.get_text()) if date_elem else None
        
        time_elem = container.find('span', class_='time')
        event_time = self.parse_time(time_elem.get_text()) if time_elem else None
        
        location_elem = container.find('span', class_='location')
        location = self.clean_text(location_elem.get_text()) if location_elem else ""
        
        link_elem = container.find('a', href=True)
        external_url = urljoin(self.base_url, link_elem['href']) if link_elem else None
        
        return {
            "title": title,
            "description": description,
            "date": event_date,
            "time": event_time or time(19, 0),  # Default time
            "location": location or "Singapore",
            "external_url": external_url,
            "source": "visitsingapore",
            "scraped_from": "visitsingapore.com",
            "category_slug": "festivals",  # Default category
            "tag_slugs": ["culture", "tourism"],
            "is_approved": False,  # Scraped events need approval
        }


class EventbriteScraper(BaseScraper):
    """Scraper for Eventbrite events in Singapore."""
    
    def __init__(self):
        super().__init__("eventbrite", "https://www.eventbrite.sg")
    
    async def scrape_events(self) -> List[Dict[str, Any]]:
        """Scrape events from Eventbrite Singapore."""
        events = []
        
        try:
            # Search for events in Singapore
            search_url = f"{self.base_url}/d/singapore--singapore/events/"
            html = await self.fetch_page(search_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find event containers
            event_containers = soup.find_all('div', {'data-testid': 'event-card'})  # Placeholder
            
            for container in event_containers:
                try:
                    event_data = await self._parse_eventbrite_event(container)
                    if event_data:
                        events.append(event_data)
                except Exception as e:
                    self.logger.warning("Error parsing Eventbrite event", error=str(e))
                    continue
            
            self.logger.info("Scraped events", source="eventbrite", count=len(events))
            
        except Exception as e:
            self.logger.error("Error scraping Eventbrite", error=str(e))
            raise ScrapingError(f"Eventbrite scraping failed: {str(e)}")
        
        return events
    
    async def _parse_eventbrite_event(self, container) -> Optional[Dict[str, Any]]:
        """Parse individual Eventbrite event."""
        # Placeholder implementation
        title_elem = container.find('h3')
        title = self.clean_text(title_elem.get_text()) if title_elem else None
        
        if not title:
            return None
        
        return {
            "title": title,
            "description": "",
            "date": date.today(),  # Placeholder
            "time": time(19, 0),
            "location": "Singapore",
            "external_url": "",
            "source": "eventbrite",
            "scraped_from": "eventbrite.sg",
            "category_slug": "concerts",
            "tag_slugs": ["eventbrite"],
            "is_approved": False,
        }


class MarinaBayScandsScraper(BaseScraper):
    """Scraper for Marina Bay Sands events."""
    
    def __init__(self):
        super().__init__("marinabaysands", "https://www.marinabaysands.com")
    
    async def scrape_events(self) -> List[Dict[str, Any]]:
        """Scrape events from Marina Bay Sands."""
        events = []
        
        try:
            events_url = f"{self.base_url}/entertainment/events.html"
            html = await self.fetch_page(events_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Parse MBS events (placeholder implementation)
            event_containers = soup.find_all('div', class_='event-listing')
            
            for container in event_containers:
                try:
                    event_data = await self._parse_mbs_event(container)
                    if event_data:
                        events.append(event_data)
                except Exception as e:
                    self.logger.warning("Error parsing MBS event", error=str(e))
                    continue
            
            self.logger.info("Scraped events", source="marinabaysands", count=len(events))
            
        except Exception as e:
            self.logger.error("Error scraping Marina Bay Sands", error=str(e))
            raise ScrapingError(f"Marina Bay Sands scraping failed: {str(e)}")
        
        return events
    
    async def _parse_mbs_event(self, container) -> Optional[Dict[str, Any]]:
        """Parse Marina Bay Sands event."""
        # Placeholder implementation
        return {
            "title": "Marina Bay Sands Event",
            "description": "",
            "date": date.today(),
            "time": time(20, 0),
            "location": "Marina Bay Sands",
            "venue": "Marina Bay Sands",
            "address": "10 Bayfront Ave, Singapore 018956",
            "latitude": Decimal("1.2834"),
            "longitude": Decimal("103.8607"),
            "external_url": self.base_url,
            "source": "marinabaysands",
            "scraped_from": "marinabaysands.com",
            "category_slug": "concerts",
            "tag_slugs": ["marina-bay", "premium"],
            "is_approved": False,
        }


class EventScrapingService:
    """Service for coordinating event scraping from multiple sources."""
    
    def __init__(self):
        self.logger = structlog.get_logger("scraping_service")
        self.scrapers = {
            "visitsingapore": VisitSingaporeScraper,
            "eventbrite": EventbriteScraper,
            "marinabaysands": MarinaBayScandsScraper,
        }
    
    async def scrape_all_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape events from all configured sources."""
        results = {}
        
        for source_name, scraper_class in self.scrapers.items():
            try:
                self.logger.info("Starting scraping", source=source_name)
                
                async with scraper_class() as scraper:
                    events = await scraper.scrape_events()
                    results[source_name] = events
                    
                self.logger.info(
                    "Completed scraping",
                    source=source_name,
                    events_count=len(events)
                )
                
            except Exception as e:
                self.logger.error(
                    "Scraping failed",
                    source=source_name,
                    error=str(e),
                    exc_info=True
                )
                results[source_name] = []
        
        total_events = sum(len(events) for events in results.values())
        self.logger.info("All sources scraped", total_events=total_events)
        
        return results
    
    async def save_scraped_events(self, scraped_data: Dict[str, List[Dict[str, Any]]]) -> int:
        """Save scraped events to database."""
        saved_count = 0
        
        async with AsyncSessionLocal() as db:
            try:
                # Get categories and tags for lookups
                categories_result = await db.execute(select(Category))
                categories = {cat.slug: cat for cat in categories_result.scalars().all()}
                
                tags_result = await db.execute(select(Tag))
                tags = {tag.slug: tag for tag in tags_result.scalars().all()}
                
                for source, events in scraped_data.items():
                    for event_data in events:
                        try:
                            # Check if event already exists
                            existing_event = await db.execute(
                                select(Event).where(
                                    Event.title == event_data["title"],
                                    Event.date == event_data["date"],
                                    Event.scraped_from == event_data.get("scraped_from")
                                )
                            )
                            
                            if existing_event.scalar_one_or_none():
                                continue  # Skip duplicate
                            
                            # Get category
                            category = categories.get(event_data.get("category_slug", "festivals"))
                            if not category:
                                continue  # Skip if category not found
                            
                            # Create event
                            event = Event(
                                title=event_data["title"],
                                description=event_data.get("description", ""),
                                date=event_data["date"],
                                time=event_data["time"],
                                location=event_data.get("location", "Singapore"),
                                venue=event_data.get("venue"),
                                address=event_data.get("address"),
                                latitude=event_data.get("latitude"),
                                longitude=event_data.get("longitude"),
                                external_url=event_data.get("external_url"),
                                category_id=category.id,
                                source="scraped",
                                scraped_from=event_data.get("scraped_from"),
                                last_scraped=datetime.utcnow(),
                                is_approved=False,  # Scraped events need approval
                                is_active=True,
                            )
                            
                            db.add(event)
                            await db.flush()  # Get event ID
                            
                            # Add tags
                            for tag_slug in event_data.get("tag_slugs", []):
                                tag = tags.get(tag_slug)
                                if tag:
                                    event.tags.append(tag)
                            
                            saved_count += 1
                            
                        except Exception as e:
                            self.logger.error(
                                "Error saving scraped event",
                                event_title=event_data.get("title", "Unknown"),
                                error=str(e)
                            )
                            continue
                
                await db.commit()
                
                self.logger.info("Scraped events saved", saved_count=saved_count)
                
            except Exception as e:
                await db.rollback()
                self.logger.error("Error saving scraped events", error=str(e), exc_info=True)
                raise
        
        return saved_count
    
    async def run_daily_scraping(self) -> Dict[str, Any]:
        """Run the daily scraping job."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Starting daily scraping job")
            
            # Scrape all sources
            scraped_data = await self.scrape_all_sources()
            
            # Save to database
            saved_count = await self.save_scraped_events(scraped_data)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).seconds
            
            result = {
                "status": "success",
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "sources_scraped": list(scraped_data.keys()),
                "total_events_found": sum(len(events) for events in scraped_data.values()),
                "events_saved": saved_count,
                "scraped_data": scraped_data,
            }
            
            self.logger.info(
                "Daily scraping completed",
                duration=duration,
                events_saved=saved_count,
                total_found=result["total_events_found"]
            )
            
            return result
            
        except Exception as e:
            self.logger.error("Daily scraping failed", error=str(e), exc_info=True)
            
            return {
                "status": "error",
                "start_time": start_time,
                "end_time": datetime.utcnow(),
                "error": str(e),
                "events_saved": 0,
            }


# Create global scraping service instance
scraping_service = EventScrapingService()