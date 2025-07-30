"""
Enhanced Suntec City scraper for mall events and conventions.

This scraper targets Suntec City events including shopping events, 
exhibitions, conventions, and community activities at the mall complex.
"""

import re
import hashlib
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from decimal import Decimal

from .base import BaseScraper, ScrapedEvent, ScrapingError


class SuntecCityScraper(BaseScraper):
    """Enhanced scraper for Suntec City events."""
    
    def __init__(self):
        super().__init__("sunteccity", "https://www.sunteccity.com.sg")
    
    async def scrape_events(self) -> List[ScrapedEvent]:
        """Scrape events from Suntec City with multiple categories."""
        events = []
        
        try:
            # Multiple event pages to check
            event_urls = [
                f"{self.base_url}/events/",
                f"{self.base_url}/whats-on/",
                f"{self.base_url}/happenings/",
                f"{self.base_url}/promotions/",
                f"{self.base_url}/suntec-convention/events/",
            ]
            
            for events_url in event_urls:
                try:
                    self.logger.info("Scraping Suntec City page", url=events_url)
                    html = await self.fetch_page(events_url)
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try multiple selectors for Suntec events
                    selectors = [
                        '.event-card',
                        '.event-item',
                        '.event-listing',
                        '.promotion-item',
                        '.happening-item',
                        '[class*="event"]',
                        '[class*="promotion"]',
                        '[class*="happening"]',
                        '.news-item'  # Sometimes events are listed as news
                    ]
                    
                    event_containers = []
                    for selector in selectors:
                        containers = soup.select(selector)
                        if containers:
                            event_containers = containers
                            self.logger.debug("Found containers", selector=selector, count=len(containers))
                            break
                    
                    # Fallback: look for any structured content
                    if not event_containers:
                        event_containers = soup.find_all(['article', 'div'], attrs={'class': re.compile(r'.*(event|promotion|happening|news).*', re.I)})
                    
                    page_events = 0
                    for container in event_containers[:self.max_events // len(event_urls)]:
                        try:
                            event = await self._parse_event_container(container, events_url)
                            if event and not self.is_duplicate_event(event):
                                events.append(event)
                                page_events += 1
                                
                                if len(events) >= self.max_events:
                                    break
                                    
                        except Exception as e:
                            self.logger.warning("Error parsing Suntec event container", error=str(e))
                            continue
                    
                    self.logger.info("Scraped Suntec page events", url=events_url, count=page_events)
                    
                    if len(events) >= self.max_events:
                        break
                        
                except Exception as e:
                    self.logger.error("Error scraping Suntec page", url=events_url, error=str(e))
                    continue
            
            self.logger.info("Scraped Suntec City events", total_count=len(events))
            
        except Exception as e:
            self.logger.error("Error scraping Suntec City", error=str(e))
            raise ScrapingError(f"Suntec City scraping failed: {str(e)}")
        
        return events
    
    async def _parse_event_container(self, container, source_url: str) -> Optional[ScrapedEvent]:
        """Parse individual Suntec City event container."""
        try:
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.event-title', '.promotion-title']
            title = None
            
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = self.clean_text(title_elem.get_text())
                    if title and len(title) > 3:
                        break
            
            if not title:
                return None
            
            # Extract description
            description_selectors = [
                '.description', '.summary', '.excerpt', '.content',
                'p', '.event-description', '.promotion-description'
            ]
            description = ""
            for selector in description_selectors:
                desc_elem = container.select_one(selector)
                if desc_elem:
                    desc_text = self.clean_text(desc_elem.get_text())
                    if desc_text and len(desc_text) > 20:
                        description = desc_text[:500]
                        break
            
            # Extract date and time information
            date_time_info = self._extract_suntec_datetime(container)
            event_date = date_time_info.get('date')
            event_time = date_time_info.get('time', time(10, 0))  # Default to 10 AM for mall events
            
            # Suntec City location details
            location_info = {
                'location': 'Suntec City',
                'venue': self._extract_suntec_venue(container),
                'address': '3 Temasek Blvd, Singapore 038983',
                'latitude': Decimal('1.2947'),
                'longitude': Decimal('103.8590')
            }
            
            # Extract external URL
            link_elem = container.find('a', href=True)
            external_url = ""
            if link_elem:
                href = link_elem['href']
                external_url = urljoin(self.base_url, href) if href.startswith('/') else href
            
            # Extract image
            image_url = self._extract_suntec_image(container)
            
            # Extract price and age restrictions
            full_text = container.get_text()
            price_info = self.extract_price_info(full_text) or self._extract_suntec_pricing(container)
            age_restrictions = self.extract_age_restrictions(full_text)
            
            # Auto-categorize and tag - Suntec events are typically shopping/business focused
            category_slug = self.categorize_event(title, description, location_info['venue'])
            tag_slugs = self.extract_tags(title, description, location_info['venue'])
            tag_slugs.extend(['suntec-city', 'shopping', 'convention'])
            
            # Determine category based on URL and content
            if 'promotion' in source_url or any(word in title.lower() for word in ['sale', 'discount', 'promotion']):
                category_slug = 'shopping'
                tag_slugs.append('promotion')
            elif 'convention' in source_url or any(word in title.lower() for word in ['conference', 'expo', 'summit']):
                category_slug = 'business'
            elif any(word in title.lower() for word in ['food', 'dining', 'restaurant']):
                category_slug = 'food'
            
            event = ScrapedEvent(
                title=title,
                description=description,
                short_description=description[:200] + '...' if len(description) > 200 else description,
                date=event_date,
                time=event_time,
                location=location_info['location'],
                venue=location_info['venue'],
                address=location_info['address'],
                latitude=location_info['latitude'],
                longitude=location_info['longitude'],
                age_restrictions=age_restrictions,
                price_info=price_info,
                external_url=external_url,
                image_url=image_url,
                category_slug=category_slug,
                tag_slugs=tag_slugs,
                source='sunteccity',
                scraped_from='sunteccity.com.sg',
                external_id=self._generate_external_id(title, event_date)
            )
            
            return event
            
        except Exception as e:
            self.logger.error("Error parsing Suntec event", error=str(e))
            return None
    
    def _extract_suntec_datetime(self, container) -> Dict[str, Any]:
        """Extract date and time information specific to Suntec format."""
        datetime_info = {'date': None, 'time': None}
        
        # Look for date/time containers
        datetime_selectors = [
            '.date', '.time', '.datetime', '.when', '.period',
            '.event-date', '.event-time', '.promotion-period',
            '[class*="date"]', '[class*="time"]'
        ]
        
        datetime_text = ""
        for selector in datetime_selectors:
            elem = container.select_one(selector)
            if elem:
                datetime_text += " " + self.clean_text(elem.get_text())
        
        if datetime_text:
            datetime_info['date'] = self.parse_date(datetime_text)
            datetime_info['time'] = self.parse_time(datetime_text)
        
        # Look for specific Suntec date formats in text
        full_text = container.get_text()
        
        # Suntec often uses formats like "Till 31 Dec" or "From 1 Jan to 31 Jan"
        period_patterns = [
            r'till\s+\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+\d{4})?',
            r'until\s+\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+\d{4})?',
            r'from\s+\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+\d{4})?\s+to\s+\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+\d{4})?'
        ]
        
        for pattern in period_patterns:
            match = re.search(pattern, full_text, re.I)
            if match and not datetime_info['date']:
                # Extract the end date for ongoing promotions
                date_part = match.group(0)
                if 'till' in date_part.lower() or 'until' in date_part.lower():
                    # Extract the end date
                    end_date_match = re.search(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\s+\d{4})?', date_part)
                    if end_date_match:
                        datetime_info['date'] = self.parse_date(end_date_match.group(0))
                break
        
        return datetime_info
    
    def _extract_suntec_venue(self, container) -> str:
        """Extract specific venue within Suntec City."""
        venue_keywords = [
            'Suntec Convention Centre', 'Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5',
            'Atrium', 'Main Entrance', 'North Wing', 'South Wing', 'East Wing', 'West Wing',
            'Food Court', 'Sky Garden', 'Convention Hall', 'Exhibition Hall'
        ]
        
        full_text = container.get_text()
        
        for keyword in venue_keywords:
            if keyword.lower() in full_text.lower():
                return keyword
        
        # Look for venue selectors
        venue_selectors = ['.venue', '.location', '.where', '.level', '[class*="venue"]', '[class*="location"]']
        for selector in venue_selectors:
            elem = container.select_one(selector)
            if elem:
                venue_text = self.clean_text(elem.get_text())
                if venue_text and len(venue_text) < 100:  # Reasonable venue name length
                    return venue_text
        
        return 'Suntec City Mall'
    
    def _extract_suntec_pricing(self, container) -> str:
        """Extract Suntec-specific pricing information."""
        # Suntec often has promotion pricing displays
        price_selectors = [
            '.price', '.pricing', '.offer', '.discount',
            '[class*="price"]', '[class*="offer"]', '[class*="discount"]'
        ]
        
        for selector in price_selectors:
            elem = container.select_one(selector)
            if elem:
                price_text = self.clean_text(elem.get_text())
                if price_text:
                    return price_text
        
        # Look for common Suntec pricing patterns
        full_text = container.get_text()
        pricing_patterns = [
            r'\d+%\s+off',
            r'up\s+to\s+\d+%\s+off',
            r'from\s+S\$\d+',
            r'S\$\d+\s*-\s*S\$\d+',
            r'free\s+admission',
            r'buy\s+\d+\s+get\s+\d+',
            r'\d+\s+for\s+S\$\d+'
        ]
        
        for pattern in pricing_patterns:
            match = re.search(pattern, full_text, re.I)
            if match:
                return self.clean_text(match.group(0))
        
        return ""
    
    def _extract_suntec_image(self, container) -> str:
        """Extract image URL from Suntec container."""
        # Try to find images
        img_elem = container.find('img')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
            if src:
                # Ensure it's a full URL
                if src.startswith('//'):
                    return f"https:{src}"
                elif src.startswith('/'):
                    return urljoin(self.base_url, src)
                else:
                    return src
        
        # Try background images
        for elem in container.find_all(['div', 'section'], style=True):
            style = elem.get('style', '')
            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
            if bg_match:
                img_url = bg_match.group(1)
                if img_url.startswith('//'):
                    return f"https:{img_url}"
                elif img_url.startswith('/'):
                    return urljoin(self.base_url, img_url)
                else:
                    return img_url
        
        return ""
    
    def _generate_external_id(self, title: str, event_date: Optional[date]) -> str:
        """Generate external ID for the event."""
        content = f"suntec|{title}|{event_date or 'no-date'}"
        return hashlib.md5(content.encode()).hexdigest()[:16]