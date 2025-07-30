"""
General utility functions and helpers.
"""

import re
import string
import secrets
from typing import Optional
from decimal import Decimal
import math


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)  # Remove special characters
    text = re.sub(r'[-\s]+', '-', text)   # Replace spaces and multiple hyphens
    text = text.strip('-')                # Remove leading/trailing hyphens
    
    return text


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def format_currency(amount: Decimal, currency: str = "SGD") -> str:
    """Format currency amount for display."""
    if currency.upper() == "SGD":
        return f"${amount:.2f} SGD"
    else:
        return f"{amount:.2f} {currency.upper()}"


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers.
    Uses the Haversine formula.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with optional suffix."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_singapore_coordinates(latitude: float, longitude: float) -> bool:
    """Validate that coordinates are within Singapore bounds."""
    # Singapore approximate bounds
    MIN_LAT, MAX_LAT = 1.16, 1.48
    MIN_LNG, MAX_LNG = 103.6, 104.0
    
    return (MIN_LAT <= latitude <= MAX_LAT and 
            MIN_LNG <= longitude <= MAX_LNG)


def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from URL."""
    if not url:
        return None
    
    import urllib.parse
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None


def clean_phone_number(phone: str) -> Optional[str]:
    """Clean and validate Singapore phone number."""
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Singapore phone number patterns
    if digits.startswith('65'):
        digits = digits[2:]  # Remove country code
    
    if len(digits) == 8:
        # Standard Singapore mobile/landline
        if digits.startswith(('6', '8', '9')):  # Valid prefixes
            return f"+65{digits}"
    
    return None


def validate_email_domain(email: str, allowed_domains: Optional[list] = None) -> bool:
    """Validate email domain against allowed list."""
    if not email or '@' not in email:
        return False
    
    if not allowed_domains:
        return True  # No restrictions
    
    domain = email.split('@')[1].lower()
    return domain in [d.lower() for d in allowed_domains]


def generate_event_reference_code() -> str:
    """Generate a unique reference code for events."""
    import datetime
    
    # Format: TSG-YYYYMMDD-XXXX (TodayAtSG - Date - Random)
    date_part = datetime.date.today().strftime('%Y%m%d')
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                         for _ in range(4))
    
    return f"TSG-{date_part}-{random_part}"


def parse_singapore_address(address: str) -> dict:
    """Parse Singapore address and extract components."""
    if not address:
        return {}
    
    # Simple parsing for Singapore addresses
    result = {"raw": address.strip()}
    
    # Extract postal code (6 digits at end)
    postal_match = re.search(r'\b(\d{6})\b', address)
    if postal_match:
        result["postal_code"] = postal_match.group(1)
    
    # Common Singapore area patterns
    areas = [
        "Orchard", "Marina Bay", "Sentosa", "Clarke Quay", "Chinatown",
        "Little India", "Bugis", "Raffles Place", "Tanjong Pagar", "Robertson Quay"
    ]
    
    for area in areas:
        if area.lower() in address.lower():
            result["area"] = area
            break
    
    return result


def format_event_datetime(date_obj, time_obj) -> str:
    """Format event date and time for display."""
    import datetime
    
    if not date_obj:
        return ""
    
    # Combine date and time
    if time_obj:
        dt = datetime.datetime.combine(date_obj, time_obj)
        return dt.strftime("%A, %B %d, %Y at %I:%M %p")
    else:
        return date_obj.strftime("%A, %B %d, %Y")


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check if request is allowed under rate limit."""
        import time
        
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old requests
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key] 
                if req_time > window_start
            ]
        else:
            self.requests[key] = []
        
        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        
        return False


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data like email addresses, phone numbers."""
    if not data or len(data) <= visible_chars:
        return data
    
    if "@" in data:  # Email
        username, domain = data.split("@", 1)
        if len(username) <= visible_chars:
            return data
        masked_username = username[:2] + mask_char * (len(username) - 4) + username[-2:]
        return f"{masked_username}@{domain}"
    else:  # Other sensitive data
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)


# Global rate limiter instance
rate_limiter = RateLimiter()