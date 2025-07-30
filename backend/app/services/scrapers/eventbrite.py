"""
Enhanced Eventbrite scraper for Singapore events.

This scraper targets Eventbrite Singapore to gather comprehensive event data
including user-generated events, corporate events, and community activities.
"""

import re
import json
import hashlib
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from decimal import Decimal

from .base import BaseScraper, ScrapedEvent, ScrapingError


class EventbriteScraper(BaseScraper):
    """Enhanced scraper for Eventbrite Singapore events."""
    
    def __init__(self):
        super().__init__("eventbrite", "https://www.eventbrite.sg")
        self.search_base = "https://www.eventbrite.sg/d/singapore--singapore/events/"
    
    async def scrape_events(self) -> List[ScrapedEvent]:
        """Scrape events from Eventbrite Singapore with category-based search."""
        events = []
        
        try:
            # Search different categories
            search_queries = [
                "",  # All events
                "?q=music",
                "?q=business", 
                "?q=food+drink",
                "?q=arts",
                "?q=sports",
                "?q=technology",
                "?q=health",
                "?q=family",
                "?q=community",
            ]
            
            for query in search_queries:
                try:
                    search_url = f"{self.search_base}{query}"
                    self.logger.info("Scraping Eventbrite search", url=search_url)
                    
                    html = await self.fetch_page(search_url)
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract JSON-LD data if available (common in Eventbrite)
                    json_events = self._extract_json_ld_events(soup)
                    for event_data in json_events:
                        try:
                            event = self._parse_json_event(event_data)
                            if event and not self.is_duplicate_event(event):
                                events.append(event)
                                if len(events) >= self.max_events:
                                    break
                        except Exception as e:
                            self.logger.warning("Error parsing JSON event", error=str(e))
                    
                    # If we have enough events from JSON, continue to next query
                    if len(events) >= self.max_events // len(search_queries):
                        continue
                    
                    # Try HTML parsing as fallback
                    selectors = [
                        '[data-testid="event-card"]',
                        '.search-event-card',
                        '.event-card',
                        '.eds-event-card',
                        '.discovery-event-card',
                        '[class*="EventCard"]'
                    ]
                    
                    event_containers = []
                    for selector in selectors:
                        containers = soup.select(selector)
                        if containers:
                            event_containers = containers
                            self.logger.debug("Found containers", selector=selector, count=len(containers))
                            break
                    
                    page_events = 0
                    for container in event_containers:
                        try:
                            event = await self._parse_event_container(container, search_url)
                            if event and not self.is_duplicate_event(event):
                                events.append(event)
                                page_events += 1
                                
                                if len(events) >= self.max_events:
                                    break
                                    
                        except Exception as e:
                            self.logger.warning("Error parsing event container", error=str(e))
                            continue
                    
                    self.logger.info("Scraped Eventbrite search results", query=query, count=page_events)
                    
                    if len(events) >= self.max_events:
                        break
                        
                except Exception as e:
                    self.logger.error("Error scraping Eventbrite search", query=query, error=str(e))
                    continue
            
            self.logger.info("Scraped Eventbrite events", total_count=len(events))
            
        except Exception as e:
            self.logger.error("Error scraping Eventbrite", error=str(e))
            raise ScrapingError(f"Eventbrite scraping failed: {str(e)}")
        
        return events
    
    def _extract_json_ld_events(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract structured data from JSON-LD scripts."""
        events = []
        
        try:
            # Find JSON-LD scripts
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle different JSON-LD structures
                    if isinstance(data, dict):
                        if data.get('@type') == 'Event':
                            events.append(data)
                        elif data.get('@type') == 'EventSeries':
                            if 'event' in data:
                                if isinstance(data['event'], list):
                                    events.extend(data['event'])
                                else:
                                    events.append(data['event'])
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get('@type') == 'Event':
                                events.append(item)
                                
                except json.JSONDecodeError as e:
                    self.logger.debug("Could not parse JSON-LD", error=str(e))
                    continue
                    
        except Exception as e:
            self.logger.warning("Error extracting JSON-LD", error=str(e))
        
        return events
    
    def _parse_json_event(self, event_data: Dict[str, Any]) -> Optional[ScrapedEvent]:
        """Parse event from JSON-LD structured data."""
        try:
            # Extract basic information
            title = event_data.get('name', '')
            if not title:
                return None
            
            description = event_data.get('description', '')
            
            # Parse dates
            start_date_str = event_data.get('startDate', '')
            event_date = None
            event_time = None
            
            if start_date_str:
                try:
                    if 'T' in start_date_str:
                        dt = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                        event_date = dt.date()
                        event_time = dt.time()
                    else:
                        event_date = datetime.fromisoformat(start_date_str).date()
                except ValueError:
                    event_date = self.parse_date(start_date_str)
            
            # Extract location
            location_data = event_data.get('location', {})
            location_name = 'Singapore'
            venue = ''
            address = ''
            
            if isinstance(location_data, dict):
                venue = location_data.get('name', '')
                if 'address' in location_data:
                    addr_data = location_data['address']
                    if isinstance(addr_data, dict):
                        address = f"{addr_data.get('streetAddress', '')} {addr_data.get('addressLocality', '')}".strip()
                    else:
                        address = str(addr_data)
                location_name = venue or address or 'Singapore'
            elif isinstance(location_data, str):
                location_name = location_data
                venue = location_data
            
            # Extract price
            price_info = ''
            offers = event_data.get('offers')
            if offers:
                if isinstance(offers, list) and offers:
                    offer = offers[0]
                elif isinstance(offers, dict):
                    offer = offers
                else:
                    offer = None
                
                if offer:
                    price = offer.get('price')
                    currency = offer.get('priceCurrency', 'SGD')
                    if price == '0' or price == 0:
                        price_info = 'Free'
                    elif price:
                        price_info = f"{currency} {price}"
            
            # Extract image
            image_url = ''
            image_data = event_data.get('image')
            if image_data:
                if isinstance(image_data, list) and image_data:
                    image_url = image_data[0] if isinstance(image_data[0], str) else image_data[0].get('url', '')
                elif isinstance(image_data, dict):
                    image_url = image_data.get('url', '')
                elif isinstance(image_data, str):
                    image_url = image_data
            
            # Extract URL
            external_url = event_data.get('url', '')
            
            # Auto-categorize and tag
            category_slug = self.categorize_event(title, description, venue)
            tag_slugs = self.extract_tags(title, description, venue)
            tag_slugs.extend(['eventbrite', 'community'])
            
            event = ScrapedEvent(
                title=self.clean_text(title),
                description=self.clean_text(description),
                short_description=self.clean_text(description)[:200] + '...' if len(description) > 200 else self.clean_text(description),
                date=event_date,
                time=event_time or time(19, 0),
                location=location_name,
                venue=venue,
                address=address,
                price_info=price_info,
                external_url=external_url,
                image_url=image_url,
                category_slug=category_slug,
                tag_slugs=tag_slugs,
                source='eventbrite',
                scraped_from='eventbrite.sg',
                external_id=self._generate_external_id(title, event_date)
            )
            
            return event
            
        except Exception as e:
            self.logger.error("Error parsing JSON event", error=str(e))
            return None
    
    async def _parse_event_container(self, container, source_url: str) -> Optional[ScrapedEvent]:
        """Parse event from HTML container."""
        try:
            # Extract title
            title_selectors = [
                '[data-testid="event-title"]',
                '.event-title',
                'h3', 'h2', 'h1',
                '[class*="title"]',
                '[class*="EventTitle"]'
            ]
            
            title = None
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = self.clean_text(title_elem.get_text())
                    if title and len(title) > 3:
                        break
            
            if not title:
                return None
            
            # Extract description/summary
            description_selectors = [
                '[data-testid="event-summary"]',
                '.event-summary',
                '.event-description',
                'p',
                '[class*="summary"]',
                '[class*="description"]'
            ]
            
            description = ""
            for selector in description_selectors:
                desc_elem = container.select_one(selector)
                if desc_elem:
                    desc_text = self.clean_text(desc_elem.get_text())
                    if desc_text and len(desc_text) > 10:
                        description = desc_text[:500]
                        break
            
            # Extract date and time
            date_time_text = self._extract_datetime_text(container)
            event_date, event_time = self._parse_eventbrite_datetime(date_time_text)
            
            # Extract location
            location_info = self._extract_eventbrite_location(container)
            
            # Extract price
            price_info = self._extract_eventbrite_price(container)
            
            # Extract URL
            link_elem = container.find('a', href=True)
            external_url = ""
            if link_elem:
                href = link_elem['href']
                external_url = urljoin(self.base_url, href) if href.startswith('/') else href
            
            # Extract image
            image_url = self._extract_eventbrite_image(container)
            
            # Auto-categorize and tag
            category_slug = self.categorize_event(title, description, location_info.get('venue', ''))
            tag_slugs = self.extract_tags(title, description, location_info.get('venue', ''))
            tag_slugs.extend(['eventbrite', 'community'])
            
            event = ScrapedEvent(
                title=title,
                description=description,
                short_description=description[:200] + '...' if len(description) > 200 else description,
                date=event_date,
                time=event_time or time(19, 0),
                location=location_info.get('location', 'Singapore'),
                venue=location_info.get('venue', ''),
                address=location_info.get('address', ''),
                price_info=price_info,
                external_url=external_url,
                image_url=image_url,
                category_slug=category_slug,
                tag_slugs=tag_slugs,
                source='eventbrite',
                scraped_from='eventbrite.sg',
                external_id=self._generate_external_id(title, event_date)
            )
            
            return event
            
        except Exception as e:
            self.logger.error("Error parsing Eventbrite event container", error=str(e))
            return None
    
    def _extract_datetime_text(self, container) -> str:
        """Extract datetime text from Eventbrite event container."""
        datetime_selectors = [
            '[data-testid="event-date-time"]',
            '.event-date-time',
            '.date-time',
            '[class*="datetime"]',
            '[class*="EventDateTime"]'
        ]
        
        for selector in datetime_selectors:
            elem = container.select_one(selector)
            if elem:
                return self.clean_text(elem.get_text())
        
        return ""
    
    def _parse_eventbrite_datetime(self, datetime_text: str) -> tuple[Optional[date], Optional[time]]:
        """Parse Eventbrite datetime format."""
        if not datetime_text:
            return None, None
        
        # Eventbrite common formats
        # "Sat, Dec 23, 2023 7:00 PM"
        # "December 23 at 7:00 PM"
        # "Today at 7:00 PM"
        
        event_date = self.parse_date(datetime_text)
        event_time = self.parse_time(datetime_text)
        
        return event_date, event_time
    
    def _extract_eventbrite_location(self, container) -> Dict[str, Any]:
        """Extract location information from Eventbrite container."""
        location_info = {
            'location': 'Singapore',
            'venue': '',
            'address': ''
        }
        
        location_selectors = [
            '[data-testid="event-location"]',
            '.event-location', 
            '.location',
            '[class*="location"]',
            '[class*="EventLocation"]'
        ]
        
        for selector in location_selectors:
            elem = container.select_one(selector)
            if elem:
                location_text = self.clean_text(elem.get_text())
                if location_text:
                    # Try to split venue and address
                    if ' • ' in location_text:
                        parts = location_text.split(' • ')
                        location_info['venue'] = parts[0]
                        location_info['address'] = parts[1] if len(parts) > 1 else ''
                    else:
                        location_info['venue'] = location_text
                    location_info['location'] = location_text
                    break
        
        return location_info
    
    def _extract_eventbrite_price(self, container) -> str:
        """Extract price information from Eventbrite container."""
        price_selectors = [
            '[data-testid="event-price"]',
            '.event-price',
            '.price',
            '[class*="price"]',
            '[class*="EventPrice"]'
        ]
        
        for selector in price_selectors:
            elem = container.select_one(selector)
            if elem:
                price_text = self.clean_text(elem.get_text())
                if price_text:
                    return price_text
        
        # Fallback: look for price patterns in all text
        full_text = container.get_text()
        return self.extract_price_info(full_text)
    
    def _extract_eventbrite_image(self, container) -> str:
        """Extract image URL from Eventbrite container."""
        # Try to find images
        img_elem = container.find('img')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
            if src and 'eventbrite' in src:
                return src
        
        return ""
    
    def _generate_external_id(self, title: str, event_date: Optional[date]) -> str:
        """Generate external ID for the event."""
        content = f"eventbrite|{title}|{event_date or 'no-date'}"
        return hashlib.md5(content.encode()).hexdigest()[:16]