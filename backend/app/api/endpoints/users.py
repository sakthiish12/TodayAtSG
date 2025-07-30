from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.core.security import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.event import Event
from app.models.review import Review
from app.schemas.auth import UserResponse
from app.schemas.event import EventResponse
from app.schemas.review import ReviewResponse

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user profile."""
    return UserResponse.from_orm(current_user)


@router.get("/my-events", response_model=List[EventResponse])
async def get_my_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_draft: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get events submitted by current user."""
    
    conditions = [Event.submitted_by_id == current_user.id]
    
    if not include_draft:
        conditions.append(Event.is_approved == True)
    
    query = select(Event).options(
        selectinload(Event.category),
        selectinload(Event.tags),
        selectinload(Event.reviews)
    ).where(
        *conditions
    ).order_by(desc(Event.created_at))
    
    # Apply pagination
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    events = result.scalars().all()
    
    return [EventResponse.from_orm(event) for event in events]


@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get reviews submitted by current user."""
    
    query = select(Review).options(
        selectinload(Review.event)
    ).where(
        Review.user_id == current_user.id
    ).order_by(desc(Review.created_at))
    
    # Apply pagination
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    reviews = result.scalars().all()
    
    # Format reviews with user name
    review_responses = []
    for review in reviews:
        review_data = ReviewResponse.from_orm(review)
        review_data.user_name = current_user.full_name
        review_responses.append(review_data)
    
    return review_responses


@router.get("/dashboard")
async def get_user_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get user dashboard statistics."""
    
    # Count user's events
    events_count_query = select(func.count(Event.id)).where(
        Event.submitted_by_id == current_user.id
    )
    events_count_result = await db.execute(events_count_query)
    total_events = events_count_result.scalar()
    
    # Count approved events
    approved_events_query = select(func.count(Event.id)).where(
        Event.submitted_by_id == current_user.id,
        Event.is_approved == True
    )
    approved_events_result = await db.execute(approved_events_query)
    approved_events = approved_events_result.scalar()
    
    # Count pending events
    pending_events = total_events - approved_events
    
    # Count user's reviews
    reviews_count_query = select(func.count(Review.id)).where(
        Review.user_id == current_user.id
    )
    reviews_count_result = await db.execute(reviews_count_query)
    total_reviews = reviews_count_result.scalar()
    
    # Get recent events
    recent_events_query = select(Event).options(
        selectinload(Event.category)
    ).where(
        Event.submitted_by_id == current_user.id
    ).order_by(desc(Event.created_at)).limit(5)
    
    recent_events_result = await db.execute(recent_events_query)
    recent_events = recent_events_result.scalars().all()
    
    # Get recent reviews
    recent_reviews_query = select(Review).options(
        selectinload(Review.event)
    ).where(
        Review.user_id == current_user.id
    ).order_by(desc(Review.created_at)).limit(5)
    
    recent_reviews_result = await db.execute(recent_reviews_query)
    recent_reviews = recent_reviews_result.scalars().all()
    
    return {
        "user": UserResponse.from_orm(current_user),
        "stats": {
            "total_events": total_events,
            "approved_events": approved_events,
            "pending_events": pending_events,
            "total_reviews": total_reviews
        },
        "recent_events": [
            {
                "id": event.id,
                "title": event.title,
                "category": event.category.name if event.category else None,
                "date": event.date,
                "is_approved": event.is_approved,
                "created_at": event.created_at
            }
            for event in recent_events
        ],
        "recent_reviews": [
            {
                "id": review.id,
                "event_title": review.event.title if review.event else "Unknown Event",
                "event_id": review.event_id,
                "rating": review.rating,
                "created_at": review.created_at
            }
            for review in recent_reviews
        ]
    }


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get detailed user statistics."""
    
    # Event statistics
    event_stats_query = select(
        func.count(Event.id).label('total'),
        func.sum(Event.view_count).label('total_views'),
        func.sum(Event.click_count).label('total_clicks')
    ).where(
        Event.submitted_by_id == current_user.id,
        Event.is_approved == True
    )
    event_stats_result = await db.execute(event_stats_query)
    event_stats = event_stats_result.first()
    
    # Review statistics
    review_stats_query = select(
        func.count(Review.id).label('total'),
        func.avg(Review.rating).label('avg_rating_given')
    ).where(Review.user_id == current_user.id)
    review_stats_result = await db.execute(review_stats_query)
    review_stats = review_stats_result.first()
    
    # Reviews received on user's events
    received_reviews_query = select(
        func.count(Review.id).label('total'),
        func.avg(Review.rating).label('avg_rating_received')
    ).join(Event, Review.event_id == Event.id).where(
        Event.submitted_by_id == current_user.id
    )
    received_reviews_result = await db.execute(received_reviews_query)
    received_reviews = received_reviews_result.first()
    
    return {
        "events": {
            "total_submitted": event_stats.total or 0,
            "total_views": event_stats.total_views or 0,
            "total_clicks": event_stats.total_clicks or 0,
            "avg_views_per_event": (event_stats.total_views / event_stats.total) if event_stats.total else 0,
        },
        "reviews": {
            "total_given": review_stats.total or 0,
            "avg_rating_given": float(review_stats.avg_rating_given) if review_stats.avg_rating_given else 0,
            "total_received": received_reviews.total or 0,
            "avg_rating_received": float(received_reviews.avg_rating_received) if received_reviews.avg_rating_received else 0,
        }
    }