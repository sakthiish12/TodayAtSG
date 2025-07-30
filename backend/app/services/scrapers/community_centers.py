"""
Singapore Community Centers scraper for grassroots and community events.

This scraper targets various Community Centers across Singapore to gather
local community events, classes, workshops, and neighborhood activities.
"""

import re
import hashlib
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from decimal import Decimal

from .base import BaseScraper, ScrapedEvent, ScrapingError


class CommunityCenter:
    """Community Center data model."""
    
    def __init__(self, name: str, url: str, area: str, address: str = "", lat: float = None, lng: float = None):
        self.name = name
        self.url = url
        self.area = area
        self.address = address
        self.latitude = Decimal(str(lat)) if lat else None
        self.longitude = Decimal(str(lng)) if lng else None


class CommunityCentersScraper(BaseScraper):
    """Enhanced scraper for Singapore Community Centers events."""
    
    def __init__(self):
        super().__init__("community_centers", "https://www.pa.gov.sg")
        
        # List of major Community Centers to scrape
        self.community_centers = [
            CommunityCenter("Ang Mo Kio CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/ang-mo-kio", "Ang Mo Kio", "53 Ang Mo Kio Ave 3, Singapore 569933", 1.3691, 103.8454),
            CommunityCenter("Bedok CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/bedok", "Bedok", "850 New Upper Changi Rd, Singapore 467352", 1.3236, 103.9273),
            CommunityCenter("Bishan CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/bishan", "Bishan", "51 Bishan Street 13, Singapore 579799", 1.3506, 103.8480),
            CommunityCenter("Bukit Batok CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/bukit-batok", "Bukit Batok", "23 Bukit Batok Central, Singapore 659526", 1.3490, 103.7498),
            CommunityCenter("Clementi CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/clementi", "Clementi", "220 Clementi Ave 4, Singapore 129880", 1.3142, 103.7649),
            CommunityCenter("Hougang CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/hougang", "Hougang", "35 Hougang Ave 3, Singapore 538840", 1.3613, 103.8929),
            CommunityCenter("Jurong West CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/jurong-west", "Jurong West", "20 Jurong West Street 93, Singapore 648965", 1.3404, 103.7090),
            CommunityCenter("Pasir Ris CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/pasir-ris", "Pasir Ris", "1 Pasir Ris Drive 4, Singapore 519457", 1.3721, 103.9474),
            CommunityCenter("Sengkang CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/sengkang", "Sengkang", "2 Sengkang Square, Singapore 545025", 1.3868, 103.8947),
            CommunityCenter("Tampines CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/tampines", "Tampines", "1 Tampines Street 86, Singapore 528651", 1.3496, 103.9568),
            CommunityCenter("Toa Payoh CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/toa-payoh", "Toa Payoh", "93 Toa Payoh Central, Singapore 319194", 1.3343, 103.8563),
            CommunityCenter("Woodlands CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/woodlands", "Woodlands", "1 Woodlands Street 83, Singapore 738520", 1.4302, 103.7890),
            CommunityCenter("Yishun CC", "https://www.pa.gov.sg/our-network/grassroots-organisations/community-clubs/yishun", "Yishun", "51 Yishun Ave 4, Singapore 768670", 1.4231, 103.8298),
        ]
    
    async def scrape_events(self) -> List[ScrapedEvent]:
        """Scrape events from multiple Community Centers."""
        all_events = []
        
        try:
            # Limit events per CC to distribute across all centers
            max_events_per_cc = max(1, self.max_events // len(self.community_centers))
            
            for cc in self.community_centers:
                try:
                    self.logger.info("Scraping Community Center", name=cc.name, area=cc.area)
                    
                    cc_events = await self._scrape_cc_events(cc, max_events_per_cc)
                    all_events.extend(cc_events)
                    
                    self.logger.info("Scraped CC events", name=cc.name, count=len(cc_events))
                    
                    if len(all_events) >= self.max_events:
                        break
                        
                except Exception as e:
                    self.logger.error("Error scraping Community Center", name=cc.name, error=str(e))
                    continue
            
            self.logger.info("Scraped Community Centers events", total_count=len(all_events))
            
        except Exception as e:
            self.logger.error("Error scraping Community Centers", error=str(e))
            raise ScrapingError(f"Community Centers scraping failed: {str(e)}")
        
        return all_events
    
    async def _scrape_cc_events(self, cc: CommunityCenter, max_events: int) -> List[ScrapedEvent]:
        """Scrape events from a specific Community Center."""
        events = []
        
        try:
            # Try multiple possible event page URLs
            event_urls = [
                f"{cc.url}/events/",
                f"{cc.url}/programmes/",
                f"{cc.url}/activities/",
                f"{cc.url}/classes/",
                f"{cc.url}/happenings/",
                cc.url  # Main page might have events
            ]
            
            for events_url in event_urls:
                try:
                    html = await self.fetch_page(events_url)
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try multiple selectors for CC events
                    selectors = [
                        '.event-card',
                        '.event-item',
                        '.programme-item',
                        '.activity-item',
                        '.class-item',
                        '[class*="event"]',
                        '[class*="programme"]',
                        '[class*="activity"]',
                        '[class*="class"]'
                    ]
                    
                    event_containers = []
                    for selector in selectors:
                        containers = soup.select(selector)
                        if containers:
                            event_containers = containers
                            break
                    
                    # Fallback: look for structured content
                    if not event_containers:
                        event_containers = soup.find_all(['div', 'article'], attrs={'class': re.compile(r'.*(event|programme|activity|class).*', re.I)})
                    
                    page_events = 0
                    for container in event_containers[:max_events]:
                        try:
                            event = await self._parse_cc_event_container(container, cc, events_url)
                            if event and not self.is_duplicate_event(event):
                                events.append(event)
                                page_events += 1
                                
                                if len(events) >= max_events:
                                    break
                                    
                        except Exception as e:
                            self.logger.warning("Error parsing CC event container", cc=cc.name, error=str(e))
                            continue
                    
                    if page_events > 0:
                        break  # Found events on this page, no need to check others
                    
                except Exception as e:
                    self.logger.debug("Error scraping CC page", cc=cc.name, url=events_url, error=str(e))
                    continue
            
        except Exception as e:
            self.logger.error("Error scraping CC events", cc=cc.name, error=str(e))
        
        return events
    
    async def _parse_cc_event_container(self, container, cc: CommunityCenter, source_url: str) -> Optional[ScrapedEvent]:
        """Parse individual Community Center event container."""
        try:
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.event-title', '.programme-title']
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
                'p', '.event-description', '.programme-description'
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
            date_time_info = self._extract_cc_datetime(container)
            event_date = date_time_info.get('date')
            event_time = date_time_info.get('time', time(19, 0))  # Default to 7 PM for community events
            
            # Use Community Center location details
            location_info = {
                'location': f"{cc.name}, {cc.area}",
                'venue': cc.name,
                'address': cc.address,
                'latitude': cc.latitude,
                'longitude': cc.longitude
            }
            
            # Extract external URL
            link_elem = container.find('a', href=True)
            external_url = ""
            if link_elem:
                href = link_elem['href']
                external_url = urljoin(self.base_url, href) if href.startswith('/') else href
            
            # Extract image
            image_url = self._extract_cc_image(container)
            
            # Extract price and age restrictions
            full_text = container.get_text()
            price_info = self.extract_price_info(full_text) or self._extract_cc_pricing(container)
            age_restrictions = self.extract_age_restrictions(full_text)
            
            # Auto-categorize and tag - CC events are typically community-focused
            category_slug = self.categorize_event(title, description, cc.name)
            tag_slugs = self.extract_tags(title, description, cc.name)
            tag_slugs.extend(['community', 'grassroots', cc.area.lower().replace(' ', '-')])
            
            # Determine category based on content
            if any(word in title.lower() for word in ['workshop', 'class', 'course', 'training']):
                category_slug = 'workshops'
            elif any(word in title.lower() for word in ['fitness', 'sports', 'exercise', 'yoga', 'zumba']):
                category_slug = 'sports'
            elif any(word in title.lower() for word in ['family', 'kids', 'children', 'toddler']):
                category_slug = 'family'
            elif any(word in title.lower() for word in ['senior', 'elderly', 'golden', 'age']):
                tag_slugs.append('seniors')
            
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
                source='community_centers',
                scraped_from='pa.gov.sg',
                external_id=self._generate_external_id(title, event_date, cc.name)
            )
            
            return event
            
        except Exception as e:
            self.logger.error("Error parsing CC event", cc=cc.name, error=str(e))
            return None
    
    def _extract_cc_datetime(self, container) -> Dict[str, Any]:
        """Extract date and time information specific to Community Center format."""
        datetime_info = {'date': None, 'time': None}
        
        # Look for date/time containers
        datetime_selectors = [
            '.date', '.time', '.datetime', '.when', '.schedule',
            '.event-date', '.event-time', '.programme-schedule',
            '[class*="date"]', '[class*="time"]', '[class*="schedule"]'
        ]
        
        datetime_text = ""
        for selector in datetime_selectors:
            elem = container.select_one(selector)
            if elem:
                datetime_text += " " + self.clean_text(elem.get_text())
        
        if datetime_text:
            datetime_info['date'] = self.parse_date(datetime_text)
            datetime_info['time'] = self.parse_time(datetime_text)
        
        # Look for specific CC date formats in text
        full_text = container.get_text()
        
        # CC often uses formats like "Every Tuesday" or "Weekly on Monday"
        recurring_patterns = [
            r'every\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'weekly\s+on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(mondays?|tuesdays?|wednesdays?|thursdays?|fridays?|saturdays?|sundays?)\s+at\s+\d',
        ]
        
        for pattern in recurring_patterns:
            match = re.search(pattern, full_text, re.I)
            if match and not datetime_info['date']:
                # For recurring events, set date to next occurrence of that day
                day_name = match.group(1) if len(match.groups()) > 0 else match.group(0).split()[0]
                datetime_info['date'] = self._get_next_weekday(day_name)
                break
        
        return datetime_info
    
    def _get_next_weekday(self, day_name: str) -> Optional[date]:
        """Get the next occurrence of a specific weekday."""
        try:
            from datetime import timedelta
            
            days = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            
            target_day = days.get(day_name.lower())
            if target_day is None:
                return None
            
            today = date.today()
            days_ahead = target_day - today.weekday()
            
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            return today + timedelta(days=days_ahead)
            
        except Exception:
            return None
    
    def _extract_cc_pricing(self, container) -> str:
        """Extract Community Center pricing information."""
        # CC events are often free or subsidized
        price_selectors = [
            '.price', '.fee', '.cost', '.charge',
            '[class*="price"]', '[class*="fee"]', '[class*="cost"]'
        ]
        
        for selector in price_selectors:
            elem = container.select_one(selector)
            if elem:
                price_text = self.clean_text(elem.get_text())
                if price_text:
                    return price_text
        
        # Look for common CC pricing patterns
        full_text = container.get_text()
        pricing_patterns = [
            r'free\s+(?:of\s+charge|admission|event)',
            r'S\$\d+\s+(?:per\s+session|per\s+person|per\s+participant)',
            r'subsidized\s+rate',
            r'member\s+rate.*S\$\d+',
            r'non-member\s+rate.*S\$\d+',
        ]
        
        for pattern in pricing_patterns:
            match = re.search(pattern, full_text, re.I)
            if match:
                return self.clean_text(match.group(0))
        
        # Default for community centers - often free
        if any(word in full_text.lower() for word in ['free', 'complimentary', 'no charge']):
            return 'Free'
        
        return ""
    
    def _extract_cc_image(self, container) -> str:
        """Extract image URL from Community Center container."""
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
        
        return ""
    
    def _generate_external_id(self, title: str, event_date: Optional[date], cc_name: str) -> str:
        """Generate external ID for the event."""
        content = f"cc|{cc_name}|{title}|{event_date or 'no-date'}"
        return hashlib.md5(content.encode()).hexdigest()[:16]