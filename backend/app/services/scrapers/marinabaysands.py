"""
Enhanced Marina Bay Sands scraper for premium events and entertainment.

This scraper targets Marina Bay Sands events including concerts, exhibitions,
dining events, and entertainment shows at the integrated resort.
"""

import re
import json
import hashlib
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from decimal import Decimal

from .base import BaseScraper, ScrapedEvent, ScrapingError


class MarinaBayScandsScraper(BaseScraper):
    """Enhanced scraper for Marina Bay Sands events."""
    
    def __init__(self):
        super().__init__("marinabaysands", "https://www.marinabaysands.com")
    
    async def scrape_events(self) -> List[ScrapedEvent]:
        """Scrape events from Marina Bay Sands with multiple categories."""
        events = []
        
        try:
            # Multiple event pages to check
            event_urls = [
                f"{self.base_url}/entertainment/events.html",
                f"{self.base_url}/entertainment/concerts-shows.html",
                f"{self.base_url}/museums-exhibitions.html",
                f"{self.base_url}/dining/events.html",
                f"{self.base_url}/shopping/events.html",
                f"{self.base_url}/sands-expo-convention-centre/events.html",
            ]
            
            for events_url in event_urls:
                try:
                    self.logger.info("Scraping Marina Bay Sands page", url=events_url)
                    html = await self.fetch_page(events_url)
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try multiple selectors for MBS events
                    selectors = [
                        '.event-card',
                        '.event-item',
                        '.event-listing',
                        '.entertainment-item',
                        '.show-listing',
                        '[class*="event"]',
                        '[class*="show"]',
                        '[data-component="event"]'
                    ]
                    
                    event_containers = []
                    for selector in selectors:
                        containers = soup.select(selector)
                        if containers:
                            event_containers = containers
                            self.logger.debug("Found containers", selector=selector, count=len(containers))
                            break
                    
                    # Fallback: look for structured content
                    if not event_containers:
                        event_containers = soup.find_all(['article', 'div'], attrs={'class': re.compile(r'.*(event|show|entertainment|exhibition).*', re.I)})
                    
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
                            self.logger.warning("Error parsing MBS event container", error=str(e))
                            continue
                    
                    self.logger.info("Scraped MBS page events", url=events_url, count=page_events)
                    
                    if len(events) >= self.max_events:
                        break
                        
                except Exception as e:
                    self.logger.error("Error scraping MBS page", url=events_url, error=str(e))
                    continue
            
            self.logger.info("Scraped Marina Bay Sands events", total_count=len(events))
            
        except Exception as e:
            self.logger.error("Error scraping Marina Bay Sands", error=str(e))
            raise ScrapingError(f"Marina Bay Sands scraping failed: {str(e)}")
        
        return events
    
    async def _parse_event_container(self, container, source_url: str) -> Optional[ScrapedEvent]:
        """Parse individual MBS event container."""
        try:
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.event-title', '.show-title']
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
                'p', '.event-description', '.show-description'
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
            date_time_info = self._extract_mbs_datetime(container)
            event_date = date_time_info.get('date')
            event_time = date_time_info.get('time', time(20, 0))  # Default to 8 PM for shows
            
            # Marina Bay Sands location details
            location_info = {
                'location': 'Marina Bay Sands',
                'venue': self._extract_mbs_venue(container),
                'address': '10 Bayfront Ave, Singapore 018956',
                'latitude': Decimal('1.2834'),
                'longitude': Decimal('103.8607')
            }
            
            # Extract external URL
            link_elem = container.find('a', href=True)
            external_url = ""
            if link_elem:
                href = link_elem['href']
                external_url = urljoin(self.base_url, href) if href.startswith('/') else href
            
            # Extract image
            image_url = self._extract_mbs_image(container)
            
            # Extract price and age restrictions
            full_text = container.get_text()
            price_info = self.extract_price_info(full_text) or self._extract_mbs_pricing(container)
            age_restrictions = self.extract_age_restrictions(full_text)
            
            # Auto-categorize and tag - MBS events are typically premium
            category_slug = self.categorize_event(title, description, location_info['venue'])
            tag_slugs = self.extract_tags(title, description, location_info['venue'])
            tag_slugs.extend(['marina-bay', 'premium', 'integrated-resort'])
            
            # Determine category based on URL and content
            if 'concert' in source_url or 'show' in source_url or any(word in title.lower() for word in ['concert', 'show', 'performance']):
                category_slug = 'concerts'
            elif 'exhibition' in source_url or 'museum' in source_url:
                category_slug = 'exhibitions'
            elif 'dining' in source_url:
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
                source='marinabaysands',
                scraped_from='marinabaysands.com',
                external_id=self._generate_external_id(title, event_date)
            )
            
            return event
            
        except Exception as e:
            self.logger.error("Error parsing MBS event", error=str(e))
            return None
    
    def _extract_mbs_datetime(self, container) -> Dict[str, Any]:
        """Extract date and time information specific to MBS format."""
        datetime_info = {'date': None, 'time': None}
        
        # Look for date/time containers
        datetime_selectors = [
            '.date', '.time', '.datetime', '.when',
            '.event-date', '.event-time', '.show-date', '.show-time',
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
        
        # Look for specific MBS date formats in text
        full_text = container.get_text()
        
        # MBS often uses formats like "20 Dec 2024" or "December 20, 2024"
        date_patterns = [
            r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, full_text, re.I)
            if match and not datetime_info['date']:
                datetime_info['date'] = self.parse_date(match.group(0))
                break
        
        return datetime_info
    
    def _extract_mbs_venue(self, container) -> str:
        """Extract specific venue within Marina Bay Sands."""
        venue_keywords = [
            'Sands Theatre', 'ArtScience Museum', 'Sands Expo', 'Convention Centre',
            'SkyPark', 'Infinity Pool', 'Casino', 'Shopping Mall', 'Food Court',
            'Roof Deck', 'Event Plaza', 'Grand Theatre', 'Studio Theatre'
        ]
        
        full_text = container.get_text()
        
        for keyword in venue_keywords:
            if keyword.lower() in full_text.lower():
                return keyword
        
        # Look for venue selectors
        venue_selectors = ['.venue', '.location', '.where', '[class*="venue"]']
        for selector in venue_selectors:
            elem = container.select_one(selector)
            if elem:
                venue_text = self.clean_text(elem.get_text())
                if venue_text and len(venue_text) < 100:  # Reasonable venue name length
                    return venue_text
        
        return 'Marina Bay Sands'
    
    def _extract_mbs_pricing(self, container) -> str:
        """Extract MBS-specific pricing information."""
        # MBS often has premium pricing displays
        price_selectors = [
            '.price', '.pricing', '.ticket-price', '.cost',
            '[class*="price"]', '[data-price]'
        ]
        
        for selector in price_selectors:
            elem = container.select_one(selector)
            if elem:
                price_text = self.clean_text(elem.get_text())
                if price_text:
                    return price_text
        
        # Look for common MBS pricing patterns
        full_text = container.get_text()
        pricing_patterns = [
            r'from\s+S\$\d+',
            r'tickets?\s+from\s+\$\d+',
            r'S\$\d+\s*-\s*S\$\d+',
            r'complimentary|free\s+admission',
            r'member\s+price.*S\$\d+'
        ]
        
        for pattern in pricing_patterns:
            match = re.search(pattern, full_text, re.I)
            if match:
                return self.clean_text(match.group(0))
        
        return ""
    
    def _extract_mbs_image(self, container) -> str:
        """Extract image URL from MBS container."""
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
        content = f"mbs|{title}|{event_date or 'no-date'}"
        return hashlib.md5(content.encode()).hexdigest()[:16]