"""
Enhanced VisitSingapore scraper for comprehensive event data extraction.

This scraper targets multiple pages on the VisitSingapore website to gather
events, festivals, and activities across Singapore with detailed information
including locations, prices, and categorization.
"""

import re
import hashlib
from typing import List, Optional, Dict, Any
from datetime import date, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from decimal import Decimal

from .base import BaseScraper, ScrapedEvent, ScrapingError


class VisitSingaporeScraper(BaseScraper):
    """Enhanced scraper for VisitSingapore events with comprehensive data extraction."""
    
    def __init__(self):
        super().__init__("visitsingapore", "https://www.visitsingapore.com")
    
    async def scrape_events(self) -> List[ScrapedEvent]:
        """Scrape events from VisitSingapore with multiple page support."""
        events = []
        
        try:
            # Multiple event pages to check
            event_urls = [
                f"{self.base_url}/see-do-singapore/events/",
                f"{self.base_url}/festivals-events-singapore/",
                f"{self.base_url}/see-do-singapore/arts-design/",
                f"{self.base_url}/see-do-singapore/entertainment/concerts-gigs/",
                f"{self.base_url}/see-do-singapore/nightlife/",
                f"{self.base_url}/see-do-singapore/food-drink/",
            ]
            
            for events_url in event_urls:
                try:
                    self.logger.info("Scraping VisitSingapore page", url=events_url)
                    html = await self.fetch_page(events_url)
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try multiple selectors as website structure may vary
                    selectors = [
                        'div[class*="event"]',
                        'article[class*="event"]',
                        'div[class*="card"]',
                        'div[class*="listing"]',
                        '.event-card',
                        '.listing-item',
                        '.attractions-item',
                        '.content-card',
                        '[data-type="attraction"]'
                    ]
                    
                    event_containers = []
                    for selector in selectors:
                        containers = soup.select(selector)
                        if containers:
                            event_containers = containers
                            self.logger.debug("Found containers", selector=selector, count=len(containers))
                            break
                    
                    if not event_containers:
                        # Fallback: look for any element with event-related keywords in class names
                        event_containers = soup.find_all(attrs={'class': re.compile(r'.*(event|activity|attraction|festival).*', re.I)})
                    
                    page_events = 0
                    for container in event_containers[:self.max_events]:  # Limit per page
                        try:
                            event = await self._parse_event_container(container, events_url)
                            if event and not self.is_duplicate_event(event):
                                events.append(event)
                                page_events += 1
                                
                                if len(events) >= self.max_events:
                                    self.logger.info("Reached max events limit", limit=self.max_events)
                                    break
                                    
                        except Exception as e:
                            self.logger.warning("Error parsing event container", error=str(e), url=events_url)
                            continue
                    
                    self.logger.info("Scraped page events", url=events_url, count=page_events)
                    
                except Exception as e:
                    self.logger.error("Error scraping VisitSingapore page", url=events_url, error=str(e))
                    continue
            
            self.logger.info("Scraped VisitSingapore events", total_count=len(events))
            
        except Exception as e:
            self.logger.error("Error scraping VisitSingapore", error=str(e))
            raise ScrapingError(f"VisitSingapore scraping failed: {str(e)}")
        
        return events
    
    async def _parse_event_container(self, container, source_url: str) -> Optional[ScrapedEvent]:
        """Parse individual event container with comprehensive data extraction."""
        try:
            # Extract title from multiple possible locations
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '[class*="title"]', '[class*="name"]']
            title = None
            
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = self.clean_text(title_elem.get_text())
                    if title and len(title) > 3:  # Valid title
                        break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = [
                '.description', '.summary', '.excerpt', 
                'p', '.content', '[class*="desc"]'
            ]
            description = ""
            for selector in description_selectors:
                desc_elem = container.select_one(selector)
                if desc_elem:
                    desc_text = self.clean_text(desc_elem.get_text())
                    if desc_text and len(desc_text) > 20:  # Substantial description
                        description = desc_text[:500]  # Limit length
                        break
            
            # Extract date and time
            date_text = self._extract_date_text(container)
            event_date = self.parse_date(date_text) if date_text else None
            
            time_text = self._extract_time_text(container)
            event_time = self.parse_time(time_text) if time_text else time(19, 0)  # Default evening time
            
            # Extract location information
            location_info = self._extract_location_info(container)
            
            # Extract external URL
            link_elem = container.find('a', href=True)
            external_url = ""
            if link_elem:
                href = link_elem['href']
                external_url = urljoin(self.base_url, href) if href.startswith('/') else href
            
            # Extract image URL
            image_url = self._extract_image_url(container)
            
            # Extract price information
            full_text = container.get_text()
            price_info = self.extract_price_info(full_text)
            age_restrictions = self.extract_age_restrictions(full_text)
            
            # Auto-categorize and tag
            category_slug = self.categorize_event(title, description, location_info.get('venue', ''))
            tag_slugs = self.extract_tags(title, description, location_info.get('venue', ''))
            tag_slugs.extend(['tourism', 'official'])  # VisitSingapore specific tags
            
            # Create event object
            event = ScrapedEvent(
                title=title,
                description=description,
                short_description=description[:200] + '...' if len(description) > 200 else description,
                date=event_date,
                time=event_time,
                location=location_info.get('location', 'Singapore'),
                venue=location_info.get('venue', ''),
                address=location_info.get('address', ''),
                latitude=location_info.get('latitude'),
                longitude=location_info.get('longitude'),
                age_restrictions=age_restrictions,
                price_info=price_info,
                external_url=external_url,
                image_url=image_url,
                category_slug=category_slug,
                tag_slugs=tag_slugs,
                source='visitsingapore',
                scraped_from='visitsingapore.com',
                external_id=self._generate_external_id(title, event_date)
            )
            
            return event
            
        except Exception as e:
            self.logger.error("Error parsing VisitSingapore event", error=str(e))
            return None
    
    def _extract_date_text(self, container) -> Optional[str]:
        """Extract date text from various possible locations."""
        date_selectors = [
            '.date', '.when', '.time', '[class*="date"]', 
            '[class*="when"]', '[class*="time"]', '.event-date'
        ]
        
        for selector in date_selectors:
            elem = container.select_one(selector)
            if elem:
                text = self.clean_text(elem.get_text())
                if text and any(char.isdigit() for char in text):
                    return text
        
        # Fallback: search in all text for date patterns
        full_text = container.get_text()
        date_patterns = [
            r'\b\d{1,2}[\s/-]\w+[\s/-]\d{2,4}\b',  # 25 Dec 2024
            r'\b\w+[\s,]+\d{1,2}[\s,]+\d{2,4}\b',  # December 25, 2024
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, full_text)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_time_text(self, container) -> Optional[str]:
        """Extract time text from various possible locations."""
        time_selectors = [
            '.time', '.when', '[class*="time"]', 
            '[data-time]', '.event-time'
        ]
        
        for selector in time_selectors:
            elem = container.select_one(selector)
            if elem:
                text = self.clean_text(elem.get_text())
                if re.search(r'\d{1,2}[:.]\d{2}|\d{1,2}\s*(am|pm)', text, re.I):
                    return text
        
        return None
    
    def _extract_location_info(self, container) -> Dict[str, Any]:
        """Extract comprehensive location information."""
        location_info = {
            'location': 'Singapore',
            'venue': '',
            'address': '',
            'latitude': None,
            'longitude': None
        }
        
        # Extract venue/location
        location_selectors = [
            '.location', '.venue', '.where', '[class*="location"]',
            '[class*="venue"]', '[class*="where"]', '.event-location'
        ]
        
        for selector in location_selectors:
            elem = container.select_one(selector)
            if elem:
                location_text = self.clean_text(elem.get_text())
                if location_text:
                    location_info['venue'] = location_text
                    location_info['location'] = location_text
                    break
        
        # Try to extract more specific address information
        address_patterns = [
            r'\d+[A-Za-z\s,]+(?:Road|Street|Avenue|Drive|Lane|Singapore)',
            r'[A-Za-z\s]+(?:Road|Street|Avenue|Drive|Lane)\s*\d*,?\s*Singapore',
        ]
        
        full_text = container.get_text()
        for pattern in address_patterns:
            match = re.search(pattern, full_text, re.I)
            if match:
                location_info['address'] = self.clean_text(match.group(0))
                break
        
        return location_info
    
    def _extract_image_url(self, container) -> str:
        """Extract image URL from container."""
        # Try to find images
        img_elem = container.find('img')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
            if src:
                return urljoin(self.base_url, src) if src.startswith('/') else src
        
        # Try background images
        for elem in container.find_all(['div', 'section'], style=True):
            style = elem.get('style', '')
            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
            if bg_match:
                return urljoin(self.base_url, bg_match.group(1))
        
        return ""
    
    def _generate_external_id(self, title: str, event_date: Optional[date]) -> str:
        """Generate external ID for the event."""
        content = f"{title}|{event_date or 'no-date'}"
        return hashlib.md5(content.encode()).hexdigest()[:16]