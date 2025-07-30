from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any
from datetime import date, datetime
import math
from sqlalchemy import select, and_, or_, func, text, desc, asc
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.core.security import get_current_user, get_current_active_user, get_current_event_organizer
from app.core.config import settings
from app.models.event import Event
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.review import Review
from app.schemas.event import (
    EventCreate, EventUpdate, EventResponse, EventListResponse,
    EventSearchRequest, EventSubmissionRequest, EventApprovalRequest
)

router = APIRouter()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


@router.post("/search", response_model=EventListResponse)
async def search_events(
    search_request: EventSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
) -> Any:
    """Advanced event search with geolocation, filtering, and sorting."""
    
    # Base query with eager loading
    query = select(Event).options(
        selectinload(Event.category),
        selectinload(Event.tags),
        selectinload(Event.reviews)
    )
    
    # Filter conditions
    conditions = [Event.is_active == True]
    
    # Only show approved events to regular users
    if not current_user or not current_user.is_admin:
        conditions.append(Event.is_approved == True)
    
    # Text search
    if search_request.search:
        search_term = f"%{search_request.search}%"
        conditions.append(
            or_(
                Event.title.ilike(search_term),
                Event.description.ilike(search_term),
                Event.short_description.ilike(search_term),
                Event.location.ilike(search_term),
                Event.venue.ilike(search_term)
            )
        )
    
    # Category filter
    if search_request.category_id:
        conditions.append(Event.category_id == search_request.category_id)
    
    # Tag filters
    if search_request.tag_ids:
        # Events that have any of the specified tags
        tag_subquery = select(Event.id).join(Event.tags).where(
            Tag.id.in_(search_request.tag_ids)
        )
        conditions.append(Event.id.in_(tag_subquery))
    
    # Date range filters
    if search_request.date_from:
        conditions.append(Event.date >= search_request.date_from)
    
    if search_request.date_to:
        conditions.append(Event.date <= search_request.date_to)
    
    # Upcoming/past events filter
    if search_request.is_upcoming is not None:
        if search_request.is_upcoming:
            conditions.append(Event.date >= date.today())
        else:
            conditions.append(Event.date < date.today())
    
    # Free events filter
    if search_request.is_free is not None:
        if search_request.is_free:
            conditions.append(
                or_(
                    Event.price_info == None,
                    Event.price_info.ilike('%free%'),
                    Event.price_info.ilike('%$0%')
                )
            )
        else:
            conditions.append(
                and_(
                    Event.price_info != None,
                    ~Event.price_info.ilike('%free%'),
                    ~Event.price_info.ilike('%$0%')
                )
            )
    
    # Apply conditions
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get all events first for distance calculation and rating filter
    all_events_result = await db.execute(query)
    all_events = all_events_result.scalars().all()
    
    # Calculate distances and apply geolocation filter
    user_lat = search_request.latitude
    user_lng = search_request.longitude
    
    if user_lat is not None and user_lng is not None:
        events_with_distance = []
        for event in all_events:
            if event.latitude and event.longitude:
                distance = calculate_distance(
                    user_lat, user_lng, 
                    float(event.latitude), float(event.longitude)
                )
                # Apply radius filter
                if search_request.radius_km is None or distance <= search_request.radius_km:
                    event.distance_km = distance
                    events_with_distance.append(event)
            else:
                # Include events without coordinates if no radius specified
                if search_request.radius_km is None:
                    event.distance_km = None
                    events_with_distance.append(event)
        all_events = events_with_distance
    else:
        # No user location provided
        for event in all_events:
            event.distance_km = None
    
    # Apply minimum rating filter
    if search_request.min_rating is not None:
        filtered_events = []
        for event in all_events:
            if event.average_rating is None or event.average_rating >= search_request.min_rating:
                filtered_events.append(event)
        all_events = filtered_events
    
    # Sort events
    if search_request.sort_by == "distance" and user_lat and user_lng:
        all_events.sort(
            key=lambda x: x.distance_km if x.distance_km is not None else float('inf'),
            reverse=(search_request.sort_order == "desc")
        )
    elif search_request.sort_by == "rating":
        all_events.sort(
            key=lambda x: x.average_rating if x.average_rating is not None else 0,
            reverse=(search_request.sort_order == "desc")
        )
    elif search_request.sort_by == "popularity":
        all_events.sort(
            key=lambda x: x.view_count + x.click_count,
            reverse=(search_request.sort_order == "desc")
        )
    elif search_request.sort_by == "created_at":
        all_events.sort(
            key=lambda x: x.created_at,
            reverse=(search_request.sort_order == "desc")
        )
    else:  # Default: sort by date
        all_events.sort(
            key=lambda x: (x.date, x.time),
            reverse=(search_request.sort_order == "desc")
        )
    
    # Apply pagination
    total = len(all_events)
    paginated_events = all_events[search_request.skip:search_request.skip + search_request.limit]
    
    # Prepare response
    search_center = None
    if user_lat and user_lng:
        search_center = {"lat": user_lat, "lng": user_lng}
    
    filters_applied = {
        "search": search_request.search,
        "category_id": search_request.category_id,
        "tag_ids": search_request.tag_ids,
        "date_from": search_request.date_from,
        "date_to": search_request.date_to,
        "radius_km": search_request.radius_km,
        "min_rating": search_request.min_rating,
        "is_free": search_request.is_free,
        "is_upcoming": search_request.is_upcoming
    }
    
    return EventListResponse(
        events=[EventResponse.from_orm(event) for event in paginated_events],
        total=total,
        skip=search_request.skip,
        limit=search_request.limit,
        has_more=search_request.skip + search_request.limit < total,
        search_center=search_center,
        filters_applied=filters_applied
    )


@router.get("/", response_model=EventListResponse)
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = None,
    approved_only: bool = True,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get list of events with basic filtering (backward compatibility)."""
    
    # Convert to search request for consistency
    search_request = EventSearchRequest(
        search=search,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        skip=skip,
        limit=limit
    )
    
    return await search_events(search_request, db)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a specific event by ID."""
    
    result = await db.execute(
        select(Event)
        .options(
            selectinload(Event.category),
            selectinload(Event.tags),
            selectinload(Event.reviews)
        )
        .where(Event.id == event_id)
    )
    
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Increment view count
    event.view_count += 1
    await db.commit()
    
    return EventResponse.from_orm(event)


@router.post("/submit", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def submit_event(
    event_data: EventSubmissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Submit a new event for approval (requires authentication)."""
    
    # Create event
    event_dict = event_data.dict(exclude={'tag_ids'})
    event = Event(
        **event_dict,
        submitted_by_id=current_user.id,
        source="user_submission",
        is_approved=False  # User submissions require approval
    )
    
    db.add(event)
    await db.flush()  # Get the event ID
    
    # Add tags if provided
    if event_data.tag_ids:
        tag_result = await db.execute(select(Tag).where(Tag.id.in_(event_data.tag_ids)))
        tags = tag_result.scalars().all()
        event.tags.extend(tags)
    
    await db.commit()
    await db.refresh(event)
    
    return EventResponse.from_orm(event)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_event_organizer),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new event directly (for event organizers and admins)."""
    
    event = Event(
        **event_data.dict(),
        submitted_by_id=current_user.id,
        source="user_submission",
        is_approved=current_user.is_admin  # Auto-approve for admins
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return EventResponse.from_orm(event)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update an existing event."""
    
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.category), selectinload(Event.tags))
        .where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check permissions
    if not current_user.is_admin and event.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this event"
        )
    
    # Update fields
    update_data = event_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    # If user submission is updated, reset approval status
    if not current_user.is_admin and event.source == "user_submission":
        event.is_approved = False
    
    await db.commit()
    await db.refresh(event)
    
    return EventResponse.from_orm(event)


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete an event."""
    
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check permissions
    if not current_user.is_admin and event.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this event"
        )
    
    await db.delete(event)
    await db.commit()
    
    return {"message": "Event deleted successfully"}


@router.post("/{event_id}/click")
async def track_event_click(
    event_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Track event click for analytics."""
    
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Increment click count
    event.click_count += 1
    await db.commit()
    
    return {"message": "Click tracked successfully"}


@router.get("/nearby", response_model=EventListResponse)
async def get_nearby_events(
    latitude: float = Query(..., description="User's latitude"),
    longitude: float = Query(..., description="User's longitude"),
    radius_km: float = Query(10.0, ge=0.1, le=100, description="Search radius in kilometers"),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get events near a specific location."""
    
    search_request = EventSearchRequest(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        category_id=category_id,
        limit=limit,
        sort_by="distance",
        is_upcoming=True
    )
    
    return await search_events(search_request, db)


@router.get("/featured", response_model=EventListResponse)
async def get_featured_events(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get featured events."""
    
    query = select(Event).options(
        selectinload(Event.category),
        selectinload(Event.tags),
        selectinload(Event.reviews)
    ).where(
        and_(
            Event.is_featured == True,
            Event.is_approved == True,
            Event.is_active == True,
            Event.date >= date.today()
        )
    ).order_by(Event.date.asc()).limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return EventListResponse(
        events=[EventResponse.from_orm(event) for event in events],
        total=len(events),
        skip=0,
        limit=limit,
        has_more=False
    )
