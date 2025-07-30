from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any
from datetime import date
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.core.security import get_current_user, get_current_active_user
from app.models.review import Review
from app.models.event import Event
from app.models.user import User
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewListResponse,
    ReviewReport, ReviewStats
)

router = APIRouter()


@router.get("/event/{event_id}", response_model=ReviewListResponse)
async def get_event_reviews(
    event_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|rating|helpful)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get reviews for a specific event."""
    
    # Check if event exists
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Build query
    query = select(Review).options(
        selectinload(Review.user)
    ).where(
        and_(
            Review.event_id == event_id,
            Review.is_reported == False  # Don't show reported reviews
        )
    )
    
    # Apply sorting
    if sort_by == "rating":
        order_col = Review.rating
    elif sort_by == "helpful":
        # For future implementation of helpful votes
        order_col = Review.created_at
    else:
        order_col = Review.created_at
    
    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(order_col)
    
    # Get total count
    count_query = select(func.count(Review.id)).where(
        and_(
            Review.event_id == event_id,
            Review.is_reported == False
        )
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    reviews = result.scalars().all()
    
    # Calculate average rating
    avg_rating_query = select(func.avg(Review.rating)).where(
        and_(
            Review.event_id == event_id,
            Review.is_reported == False
        )
    )
    avg_result = await db.execute(avg_rating_query)
    average_rating = avg_result.scalar()
    
    # Format reviews with user names
    review_responses = []
    for review in reviews:
        review_data = ReviewResponse.from_orm(review)
        review_data.user_name = review.user.full_name
        review_responses.append(review_data)
    
    return ReviewListResponse(
        reviews=review_responses,
        total=total,
        skip=skip,
        limit=limit,
        average_rating=float(average_rating) if average_rating else None
    )


@router.get("/event/{event_id}/stats", response_model=ReviewStats)
async def get_event_review_stats(
    event_id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get review statistics for an event."""
    
    # Check if event exists
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Get total count and average rating
    stats_query = select(
        func.count(Review.id).label('total'),
        func.avg(Review.rating).label('avg_rating')
    ).where(
        and_(
            Review.event_id == event_id,
            Review.is_reported == False
        )
    )
    stats_result = await db.execute(stats_query)
    stats = stats_result.first()
    
    # Get rating distribution
    distribution_query = select(
        Review.rating,
        func.count(Review.id).label('count')
    ).where(
        and_(
            Review.event_id == event_id,
            Review.is_reported == False
        )
    ).group_by(Review.rating).order_by(Review.rating)
    
    distribution_result = await db.execute(distribution_query)
    distribution_rows = distribution_result.all()
    
    # Create rating distribution dict
    rating_distribution = {i: 0 for i in range(1, 6)}
    for row in distribution_rows:
        rating_distribution[row.rating] = row.count
    
    # Get recent reviews
    recent_query = select(Review).options(
        selectinload(Review.user)
    ).where(
        and_(
            Review.event_id == event_id,
            Review.is_reported == False
        )
    ).order_by(desc(Review.created_at)).limit(5)
    
    recent_result = await db.execute(recent_query)
    recent_reviews = recent_result.scalars().all()
    
    # Format recent reviews
    recent_review_responses = []
    for review in recent_reviews:
        review_data = ReviewResponse.from_orm(review)
        review_data.user_name = review.user.full_name
        recent_review_responses.append(review_data)
    
    return ReviewStats(
        total_reviews=stats.total,
        average_rating=float(stats.avg_rating) if stats.avg_rating else None,
        rating_distribution=rating_distribution,
        recent_reviews=recent_review_responses
    )


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new review for an event."""
    
    # Check if event exists
    event_result = await db.execute(select(Event).where(Event.id == review_data.event_id))
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user already reviewed this event
    existing_review_result = await db.execute(
        select(Review).where(
            and_(
                Review.user_id == current_user.id,
                Review.event_id == review_data.event_id
            )
        )
    )
    existing_review = existing_review_result.scalar_one_or_none()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this event"
        )
    
    # Create review
    review = Review(
        user_id=current_user.id,
        event_id=review_data.event_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    # Load user relationship
    await db.refresh(review, ['user'])
    
    review_response = ReviewResponse.from_orm(review)
    review_response.user_name = current_user.full_name
    
    return review_response


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update an existing review."""
    
    result = await db.execute(
        select(Review).options(selectinload(Review.user))
        .where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check permissions
    if review.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this review"
        )
    
    # Update fields
    update_data = review_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    await db.commit()
    await db.refresh(review)
    
    review_response = ReviewResponse.from_orm(review)
    review_response.user_name = review.user.full_name
    
    return review_response


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a review."""
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check permissions
    if review.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this review"
        )
    
    await db.delete(review)
    await db.commit()
    
    return {"message": "Review deleted successfully"}


@router.post("/{review_id}/report")
async def report_review(
    review_id: int,
    report_data: ReviewReport,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Report a review for inappropriate content."""
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Can't report your own review
    if review.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot report your own review"
        )
    
    # Increment report count
    review.report_count += 1
    
    # Auto-hide if too many reports
    if review.report_count >= 5:
        review.is_reported = True
    
    # TODO: Create a report record for admin review
    # TODO: Send notification to admins
    
    await db.commit()
    
    return {"message": "Review reported successfully"}


@router.get("/user/my-reviews", response_model=ReviewListResponse)
async def get_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get current user's reviews."""
    
    # Get user's reviews
    query = select(Review).options(
        selectinload(Review.event)
    ).where(
        Review.user_id == current_user.id
    ).order_by(desc(Review.created_at))
    
    # Get total count
    count_query = select(func.count(Review.id)).where(Review.user_id == current_user.id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    reviews = result.scalars().all()
    
    # Format reviews
    review_responses = []
    for review in reviews:
        review_data = ReviewResponse.from_orm(review)
        review_data.user_name = current_user.full_name
        review_responses.append(review_data)
    
    return ReviewListResponse(
        reviews=review_responses,
        total=total,
        skip=skip,
        limit=limit
    )