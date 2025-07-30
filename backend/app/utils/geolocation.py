"""
Geolocation utilities for TodayAtSG

This module provides utilities for geolocation-based searches, distance calculations,
and spatial queries optimized for Singapore's geography.
"""

import math
from typing import List, Tuple, Optional
from decimal import Decimal
from sqlalchemy import and_, or_, text, func
from sqlalchemy.orm import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


# Singapore bounds for validation
SINGAPORE_BOUNDS = {
    'min_lat': 1.2,
    'max_lat': 1.5,
    'min_lng': 103.6,
    'max_lng': 104.0
}

# Popular Singapore locations for quick reference
SINGAPORE_LOCATIONS = {
    'marina_bay': {'lat': 1.2806, 'lng': 103.8598, 'name': 'Marina Bay'},
    'orchard': {'lat': 1.3048, 'lng': 103.8318, 'name': 'Orchard Road'},
    'clarke_quay': {'lat': 1.2884, 'lng': 103.8470, 'name': 'Clarke Quay'},
    'sentosa': {'lat': 1.2494, 'lng': 103.8303, 'name': 'Sentosa Island'},
    'chinatown': {'lat': 1.2820, 'lng': 103.8439, 'name': 'Chinatown'},
    'little_india': {'lat': 1.3067, 'lng': 103.8524, 'name': 'Little India'},
    'bugis': {'lat': 1.2966, 'lng': 103.8520, 'name': 'Bugis'},
    'raffles_place': {'lat': 1.2834, 'lng': 103.8519, 'name': 'Raffles Place'},
    'city_hall': {'lat': 1.2930, 'lng': 103.8520, 'name': 'City Hall'},
    'harbourfront': {'lat': 1.2653, 'lng': 103.8220, 'name': 'HarbourFront'},
    'jurong_east': {'lat': 1.3329, 'lng': 103.7436, 'name': 'Jurong East'},
    'tampines': {'lat': 1.3496, 'lng': 103.9568, 'name': 'Tampines'},
    'woodlands': {'lat': 1.4382, 'lng': 103.7890, 'name': 'Woodlands'},
    'changi': {'lat': 1.3644, 'lng': 103.9915, 'name': 'Changi'},
}


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1, lng1: Latitude and longitude of first point (in decimal degrees)
        lat2, lng2: Latitude and longitude of second point (in decimal degrees)
    
    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r


def get_bounding_box(lat: float, lng: float, radius_km: float) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box coordinates for a given point and radius.
    
    This is used to optimize database queries by filtering to approximate bounds
    before calculating exact distances.
    
    Args:
        lat: Center latitude
        lng: Center longitude
        radius_km: Search radius in kilometers
    
    Returns:
        Tuple of (min_lat, max_lat, min_lng, max_lng)
    """
    # Approximate conversion: 1 degree ≈ 111 km
    lat_delta = radius_km / 111.0
    
    # Longitude delta varies with latitude
    lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
    
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lng = lng - lng_delta
    max_lng = lng + lng_delta
    
    return min_lat, max_lat, min_lng, max_lng


def is_within_singapore(lat: float, lng: float) -> bool:
    """
    Check if coordinates are within Singapore bounds.
    
    Args:
        lat: Latitude
        lng: Longitude
    
    Returns:
        True if coordinates are within Singapore
    """
    return (SINGAPORE_BOUNDS['min_lat'] <= lat <= SINGAPORE_BOUNDS['max_lat'] and
            SINGAPORE_BOUNDS['min_lng'] <= lng <= SINGAPORE_BOUNDS['max_lng'])


def get_nearest_singapore_location(lat: float, lng: float) -> Optional[dict]:
    """
    Find the nearest popular Singapore location to given coordinates.
    
    Args:
        lat: Latitude
        lng: Longitude
    
    Returns:
        Dictionary with nearest location info or None
    """
    if not is_within_singapore(lat, lng):
        return None
    
    nearest_location = None
    min_distance = float('inf')
    
    for location_key, location_data in SINGAPORE_LOCATIONS.items():
        distance = haversine_distance(lat, lng, location_data['lat'], location_data['lng'])
        if distance < min_distance:
            min_distance = distance
            nearest_location = {
                'key': location_key,
                'name': location_data['name'],
                'lat': location_data['lat'],
                'lng': location_data['lng'],
                'distance_km': distance
            }
    
    return nearest_location


async def find_nearby_events(
    db: AsyncSession,
    center_lat: float,
    center_lng: float,
    radius_km: float = 10.0,
    limit: int = 50,
    category_id: Optional[int] = None,
    is_approved: bool = True,
    is_active: bool = True
) -> List[dict]:
    """
    Find events within a specified radius of a location.
    
    This function uses a two-step approach:
    1. Filter by bounding box (fast)
    2. Calculate exact distances (precise)
    
    Args:
        db: Async database session
        center_lat: Center latitude
        center_lng: Center longitude
        radius_km: Search radius in kilometers
        limit: Maximum number of results
        category_id: Optional category filter
        is_approved: Filter for approved events
        is_active: Filter for active events
    
    Returns:
        List of event dictionaries with distance information
    """
    # Get bounding box for initial filtering
    min_lat, max_lat, min_lng, max_lng = get_bounding_box(center_lat, center_lng, radius_km)
    
    # Build query with bounding box filter
    query = db.query(Event).filter(
        and_(
            Event.latitude.between(min_lat, max_lat),
            Event.longitude.between(min_lng, max_lng),
            Event.latitude.isnot(None),
            Event.longitude.isnot(None),
            Event.is_approved == is_approved,
            Event.is_active == is_active
        )
    )
    
    # Add category filter if specified
    if category_id:
        query = query.filter(Event.category_id == category_id)
    
    # Execute query
    events = await query.limit(limit * 2).all()  # Get extra to account for distance filtering
    
    # Calculate exact distances and filter
    nearby_events = []
    for event in events:
        if event.latitude and event.longitude:
            distance = haversine_distance(
                center_lat, center_lng,
                float(event.latitude), float(event.longitude)
            )
            
            if distance <= radius_km:
                event_dict = {
                    'id': event.id,
                    'title': event.title,
                    'short_description': event.short_description,
                    'date': event.date,
                    'time': event.time,
                    'location': event.location,
                    'venue': event.venue,
                    'latitude': float(event.latitude),
                    'longitude': float(event.longitude),
                    'distance_km': round(distance, 2),
                    'category_id': event.category_id,
                    'price_info': event.price_info,
                    'external_url': event.external_url,
                    'image_url': event.image_url
                }
                nearby_events.append(event_dict)
    
    # Sort by distance and limit results
    nearby_events.sort(key=lambda x: x['distance_km'])
    return nearby_events[:limit]


async def get_events_by_location_name(
    db: AsyncSession,
    location_name: str,
    radius_km: float = 5.0,
    limit: int = 20
) -> List[dict]:
    """
    Find events near a named Singapore location.
    
    Args:
        db: Async database session
        location_name: Name or key of Singapore location
        radius_km: Search radius in kilometers
        limit: Maximum number of results
    
    Returns:
        List of nearby events
    """
    # Try to find location by key or name
    location_data = None
    location_name_lower = location_name.lower().replace(' ', '_').replace('-', '_')
    
    # Check exact key match
    if location_name_lower in SINGAPORE_LOCATIONS:
        location_data = SINGAPORE_LOCATIONS[location_name_lower]
    else:
        # Check name match
        for key, data in SINGAPORE_LOCATIONS.items():
            if location_name.lower() in data['name'].lower():
                location_data = data
                break
    
    if not location_data:
        return []
    
    return await find_nearby_events(
        db=db,
        center_lat=location_data['lat'],
        center_lng=location_data['lng'],
        radius_km=radius_km,
        limit=limit
    )


def create_geolocation_query_filter(
    query: Query,
    center_lat: float,
    center_lng: float,
    radius_km: float
) -> Query:
    """
    Add geolocation filtering to an existing SQLAlchemy query.
    
    This is useful for adding location-based filtering to complex queries
    that already have other filters applied.
    
    Args:
        query: Existing SQLAlchemy query
        center_lat: Center latitude
        center_lng: Center longitude
        radius_km: Search radius in kilometers
    
    Returns:
        Modified query with geolocation filters
    """
    min_lat, max_lat, min_lng, max_lng = get_bounding_box(center_lat, center_lng, radius_km)
    
    return query.filter(
        and_(
            Event.latitude.between(min_lat, max_lat),
            Event.longitude.between(min_lng, max_lng),
            Event.latitude.isnot(None),
            Event.longitude.isnot(None)
        )
    )


def get_location_suggestions(search_term: str) -> List[dict]:
    """
    Get location suggestions based on search term.
    
    Args:
        search_term: User's search input
    
    Returns:
        List of matching Singapore locations
    """
    suggestions = []
    search_lower = search_term.lower()
    
    for key, data in SINGAPORE_LOCATIONS.items():
        if (search_lower in data['name'].lower() or 
            search_lower in key.replace('_', ' ')):
            suggestions.append({
                'key': key,
                'name': data['name'],
                'lat': data['lat'],
                'lng': data['lng']
            })
    
    return suggestions


def calculate_area_center(events: List[dict]) -> Optional[dict]:
    """
    Calculate the geographic center of a list of events.
    
    This is useful for determining the optimal map center when displaying
    multiple events.
    
    Args:
        events: List of event dictionaries with lat/lng
    
    Returns:
        Dictionary with center coordinates or None
    """
    if not events:
        return None
    
    valid_events = [e for e in events if 'latitude' in e and 'longitude' in e and 
                   e['latitude'] is not None and e['longitude'] is not None]
    
    if not valid_events:
        return None
    
    total_lat = sum(float(e['latitude']) for e in valid_events)
    total_lng = sum(float(e['longitude']) for e in valid_events)
    
    center_lat = total_lat / len(valid_events)
    center_lng = total_lng / len(valid_events)
    
    return {
        'lat': center_lat,
        'lng': center_lng,
        'event_count': len(valid_events)
    }


def get_distance_display_text(distance_km: float) -> str:
    """
    Get user-friendly display text for distances.
    
    Args:
        distance_km: Distance in kilometers
    
    Returns:
        Formatted distance string
    """
    if distance_km < 0.1:
        return "< 100m"
    elif distance_km < 1:
        return f"{int(distance_km * 1000)}m"
    elif distance_km < 10:
        return f"{distance_km:.1f}km"
    else:
        return f"{int(distance_km)}km"


class GeolocationService:
    """Service class for geolocation operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search_nearby(
        self,
        lat: float,
        lng: float,
        radius_km: float = 10.0,
        filters: dict = None
    ) -> dict:
        """
        Comprehensive nearby search with filtering and metadata.
        
        Args:
            lat: Center latitude
            lng: Center longitude
            radius_km: Search radius
            filters: Additional filters (category, date range, etc.)
        
        Returns:
            Dictionary with events, metadata, and suggestions
        """
        if not is_within_singapore(lat, lng):
            return {
                'events': [],
                'center': {'lat': lat, 'lng': lng},
                'error': 'Location is outside Singapore'
            }
        
        # Find nearby events
        events = await find_nearby_events(
            db=self.db,
            center_lat=lat,
            center_lng=lng,
            radius_km=radius_km,
            limit=filters.get('limit', 50) if filters else 50,
            category_id=filters.get('category_id') if filters else None
        )
        
        # Get nearest landmark
        nearest_location = get_nearest_singapore_location(lat, lng)
        
        return {
            'events': events,
            'center': {'lat': lat, 'lng': lng},
            'radius_km': radius_km,
            'total_found': len(events),
            'nearest_location': nearest_location,
            'search_area': {
                'min_lat': lat - radius_km/111,
                'max_lat': lat + radius_km/111,
                'min_lng': lng - radius_km/(111*math.cos(math.radians(lat))),
                'max_lng': lng + radius_km/(111*math.cos(math.radians(lat)))
            }
        }