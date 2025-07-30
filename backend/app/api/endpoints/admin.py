from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any
from datetime import date, datetime
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.core.security import get_current_admin_user
from app.models.event import Event
from app.models.user import User
from app.models.review import Review
from app.models.category import Category
from app.models.tag import Tag
from app.schemas.event import EventResponse, EventListResponse, EventApprovalRequest
from app.schemas.auth import UserResponse
from app.schemas.review import ReviewResponse

router = APIRouter()


@router.get("/events/pending", response_model=EventListResponse)
async def get_pending_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all pending events awaiting approval."""
    
    query = select(Event).options(
        selectinload(Event.category),
        selectinload(Event.tags),
        selectinload(Event.submitted_by)
    ).where(
        and_(
            Event.is_approved == False,
            Event.source == "user_submission"
        )
    ).order_by(Event.created_at.asc())
    
    # Get total count
    count_query = select(func.count(Event.id)).where(
        and_(
            Event.is_approved == False,
            Event.source == "user_submission"
        )
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    events = result.scalars().all()
    
    return EventListResponse(
        events=[EventResponse.from_orm(event) for event in events],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )


@router.post("/events/{event_id}/approve")
async def approve_or_reject_event(
    event_id: int,
    approval_data: EventApprovalRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Approve or reject a pending event."""
    
    result = await db.execute(
        select(Event).options(selectinload(Event.submitted_by))
        .where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Update event approval status
    event.is_approved = approval_data.approved
    
    if approval_data.approved:
        # If approved, make it active
        event.is_active = True
    else:
        # If rejected, deactivate it
        event.is_active = False
    
    # TODO: Add admin notes field to Event model
    # event.admin_notes = approval_data.admin_notes
    # event.rejection_reason = approval_data.rejection_reason
    
    await db.commit()
    
    # TODO: Send notification email to event submitter
    
    status_text = "approved" if approval_data.approved else "rejected"
    return {"message": f"Event {status_text} successfully"}


@router.get("/events/all", response_model=EventListResponse)
async def get_all_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_inactive: bool = Query(False),
    include_unapproved: bool = Query(True),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all events for admin management."""
    
    # Build conditions
    conditions = []
    
    if not include_inactive:
        conditions.append(Event.is_active == True)
    
    if not include_unapproved:
        conditions.append(Event.is_approved == True)
    
    query = select(Event).options(
        selectinload(Event.category),
        selectinload(Event.tags),
        selectinload(Event.submitted_by),
        selectinload(Event.reviews)
    )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(desc(Event.created_at))
    
    # Get total count
    count_query = select(func.count(Event.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    events = result.scalars().all()
    
    return EventListResponse(
        events=[EventResponse.from_orm(event) for event in events],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )


@router.post("/events/{event_id}/feature")
async def toggle_event_featured(
    event_id: int,
    featured: bool = True,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Toggle event featured status."""
    
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    event.is_featured = featured
    await db.commit()
    
    status_text = "featured" if featured else "unfeatured"
    return {"message": f"Event {status_text} successfully"}


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_inactive: bool = Query(False),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all users for admin management."""
    
    query = select(User)
    
    if not include_inactive:
        query = query.where(User.is_active == True)
    
    query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [UserResponse.from_orm(user) for user in users]


@router.post("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    active: bool = True,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Toggle user active status."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )
    
    user.is_active = active
    await db.commit()
    
    status_text = "activated" if active else "deactivated"
    return {"message": f"User {status_text} successfully"}


@router.post("/users/{user_id}/make-organizer")
async def toggle_user_organizer(
    user_id: int,
    is_organizer: bool = True,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Toggle user event organizer status."""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_event_organizer = is_organizer
    await db.commit()
    
    status_text = "granted organizer privileges" if is_organizer else "removed organizer privileges"
    return {"message": f"User {status_text} successfully"}


@router.get("/reviews/reported", response_model=List[ReviewResponse])
async def get_reported_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all reported reviews for moderation."""
    
    query = select(Review).options(
        selectinload(Review.user),
        selectinload(Review.event)
    ).where(
        or_(
            Review.is_reported == True,
            Review.report_count > 0
        )
    ).order_by(desc(Review.report_count), desc(Review.created_at))
    
    # Apply pagination
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    reviews = result.scalars().all()
    
    # Format reviews with user names
    review_responses = []
    for review in reviews:
        review_data = ReviewResponse.from_orm(review)
        review_data.user_name = review.user.full_name
        review_responses.append(review_data)
    
    return review_responses


@router.post("/reviews/{review_id}/moderate")
async def moderate_review(
    review_id: int,
    action: str = Query(..., regex="^(approve|hide|delete)$"),
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Moderate a reported review."""
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if action == "approve":
        # Clear reports and unhide
        review.is_reported = False
        review.report_count = 0
        message = "Review approved and unhidden"
    elif action == "hide":
        # Hide the review
        review.is_reported = True
        message = "Review hidden from public view"
    elif action == "delete":
        # Delete the review permanently
        await db.delete(review)
        await db.commit()
        return {"message": "Review deleted permanently"}
    
    await db.commit()
    return {"message": message}


@router.get("/stats/dashboard")
async def get_admin_dashboard_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get admin dashboard statistics."""
    
    # Event statistics
    total_events_query = select(func.count(Event.id))
    total_events_result = await db.execute(total_events_query)
    total_events = total_events_result.scalar()
    
    pending_events_query = select(func.count(Event.id)).where(
        and_(Event.is_approved == False, Event.source == "user_submission")
    )
    pending_events_result = await db.execute(pending_events_query)
    pending_events = pending_events_result.scalar()
    
    active_events_query = select(func.count(Event.id)).where(
        and_(Event.is_active == True, Event.date >= date.today())
    )
    active_events_result = await db.execute(active_events_query)
    active_events = active_events_result.scalar()
    
    # User statistics
    total_users_query = select(func.count(User.id))
    total_users_result = await db.execute(total_users_query)
    total_users = total_users_result.scalar()
    
    active_users_query = select(func.count(User.id)).where(User.is_active == True)
    active_users_result = await db.execute(active_users_query)
    active_users = active_users_result.scalar()
    
    organizers_query = select(func.count(User.id)).where(
        and_(User.is_event_organizer == True, User.is_active == True)
    )
    organizers_result = await db.execute(organizers_query)
    organizers = organizers_result.scalar()
    
    # Review statistics
    total_reviews_query = select(func.count(Review.id))
    total_reviews_result = await db.execute(total_reviews_query)
    total_reviews = total_reviews_result.scalar()
    
    reported_reviews_query = select(func.count(Review.id)).where(
        or_(Review.is_reported == True, Review.report_count > 0)
    )
    reported_reviews_result = await db.execute(reported_reviews_query)
    reported_reviews = reported_reviews_result.scalar()
    
    # Recent activity
    recent_events_query = select(Event).options(
        selectinload(Event.category)
    ).where(
        Event.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).order_by(desc(Event.created_at)).limit(5)
    
    recent_events_result = await db.execute(recent_events_query)
    recent_events_list = recent_events_result.scalars().all()
    
    return {
        "events": {
            "total": total_events,
            "pending": pending_events,
            "active": active_events
        },
        "users": {
            "total": total_users,
            "active": active_users,
            "organizers": organizers
        },
        "reviews": {
            "total": total_reviews,
            "reported": reported_reviews
        },
        "recent_events": [
            {
                "id": event.id,
                "title": event.title,
                "category": event.category.name if event.category else None,
                "created_at": event.created_at,
                "is_approved": event.is_approved
            }
            for event in recent_events_list
        ]
    }