from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum

from app.schemas.category import CategoryResponse


class TagResponse(BaseModel):
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True


class EventSource(str, Enum):
    USER_SUBMISSION = "user_submission"
    SCRAPED = "scraped"
    ADMIN = "admin"


class EventStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    date: date
    time: time
    end_date: Optional[date] = None
    end_time: Optional[time] = None
    location: str
    venue: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    age_restrictions: Optional[str] = None
    price_info: Optional[str] = None
    external_url: Optional[str] = None
    image_url: Optional[str] = None
    category_id: int
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        if len(v) > 255:
            raise ValueError('Title must be less than 255 characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 5000:
                raise ValueError('Description must be less than 5000 characters')
        return v
    
    @validator('short_description')
    def validate_short_description(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 500:
                raise ValueError('Short description must be less than 500 characters')
        return v
    
    @validator('location')
    def validate_location(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Location must be at least 3 characters long')
        return v.strip()
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v
    
    @validator('external_url')
    def validate_external_url(cls, v):
        if v is not None and not v.startswith(('http://', 'https://')):
            raise ValueError('External URL must be a valid HTTP/HTTPS URL')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    date: Optional[date] = None
    time: Optional[time] = None
    end_date: Optional[date] = None
    end_time: Optional[time] = None
    location: Optional[str] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    age_restrictions: Optional[str] = None
    price_info: Optional[str] = None
    external_url: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None


class EventResponse(EventBase):
    id: int
    is_approved: bool
    is_featured: bool
    is_active: bool
    source: str
    created_at: datetime
    updated_at: datetime
    view_count: int
    click_count: int
    average_rating: Optional[float] = None
    review_count: int = 0
    distance_km: Optional[float] = None  # Distance from user location
    is_upcoming: bool
    is_past: bool
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


class EventSearchRequest(BaseModel):
    search: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = None
    min_rating: Optional[float] = None
    is_free: Optional[bool] = None
    is_upcoming: Optional[bool] = True
    sort_by: Optional[str] = "date"  # date, rating, distance, popularity
    sort_order: Optional[str] = "asc"  # asc, desc
    skip: int = 0
    limit: int = 20
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v
    
    @validator('radius_km')
    def validate_radius(cls, v):
        if v is not None and (v < 0.1 or v > 100):
            raise ValueError('Radius must be between 0.1 and 100 km')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        valid_sorts = ['date', 'rating', 'distance', 'popularity', 'created_at']
        if v not in valid_sorts:
            raise ValueError(f'Sort by must be one of: {valid_sorts}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
    search_center: Optional[dict] = None  # {lat: float, lng: float}
    filters_applied: dict = {}


class EventSubmissionRequest(EventBase):
    tag_ids: Optional[List[int]] = None
    

class EventApprovalRequest(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None
    admin_notes: Optional[str] = None
