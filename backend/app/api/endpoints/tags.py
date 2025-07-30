from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.core.security import get_current_admin_user, get_current_user
from app.models.tag import Tag
from app.models.event import Event
from app.models.event_tag import event_tags
from app.schemas.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter()


@router.get("/", response_model=List[TagResponse])
async def get_tags(
    include_event_count: bool = Query(False),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all tags with optional filtering and event counts."""
    
    if include_event_count:
        # Query with event count
        query = select(
            Tag,
            func.count(Event.id).label('event_count')
        ).outerjoin(
            event_tags, event_tags.c.tag_id == Tag.id
        ).outerjoin(
            Event,
            and_(
                Event.id == event_tags.c.event_id,
                Event.is_approved == True,
                Event.is_active == True
            )
        ).group_by(Tag.id)
    else:
        query = select(Tag)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(Tag.name.ilike(search_term))
    
    # Apply ordering
    if include_event_count:
        query = query.order_by(desc('event_count'), Tag.name)
    else:
        query = query.order_by(Tag.name)
    
    # Apply limit
    if limit:
        query = query.limit(limit)
    
    result = await db.execute(query)
    
    if include_event_count:
        rows = result.all()
        tags = []
        for row in rows:
            tag_data = TagResponse.from_orm(row.Tag)
            tag_data.event_count = row.event_count
            tags.append(tag_data)
        return tags
    else:
        tags = result.scalars().all()
        return [TagResponse.from_orm(tag) for tag in tags]


@router.get("/popular", response_model=List[TagResponse])
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get tags ordered by number of events."""
    
    query = select(
        Tag,
        func.count(Event.id).label('event_count')
    ).outerjoin(
        event_tags, event_tags.c.tag_id == Tag.id
    ).outerjoin(
        Event,
        and_(
            Event.id == event_tags.c.event_id,
            Event.is_approved == True,
            Event.is_active == True
        )
    ).group_by(Tag.id).having(
        func.count(Event.id) > 0
    ).order_by(
        desc('event_count'),
        Tag.name
    ).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    tags = []
    for row in rows:
        tag_data = TagResponse.from_orm(row.Tag)
        tag_data.event_count = row.event_count
        tags.append(tag_data)
    
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    include_event_count: bool = Query(False),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a specific tag by ID."""
    
    if include_event_count:
        query = select(
            Tag,
            func.count(Event.id).label('event_count')
        ).outerjoin(
            event_tags, event_tags.c.tag_id == Tag.id
        ).outerjoin(
            Event,
            and_(
                Event.id == event_tags.c.event_id,
                Event.is_approved == True,
                Event.is_active == True
            )
        ).where(Tag.id == tag_id).group_by(Tag.id)
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        tag_data = TagResponse.from_orm(row.Tag)
        tag_data.event_count = row.event_count
        
        return tag_data
    else:
        result = await db.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        return TagResponse.from_orm(tag)


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_admin = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new tag (admin only)."""
    
    # Check if tag already exists
    result = await db.execute(
        select(Tag).where(
            or_(
                Tag.name == tag_data.name,
                Tag.slug == tag_data.slug
            )
        )
    )
    existing_tag = result.scalar_one_or_none()
    
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name or slug already exists"
        )
    
    tag = Tag(**tag_data.dict())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return TagResponse.from_orm(tag)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    current_admin = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update an existing tag (admin only)."""
    
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check for duplicate name/slug if being updated
    update_data = tag_data.dict(exclude_unset=True)
    if 'name' in update_data or 'slug' in update_data:
        conditions = []
        if 'name' in update_data:
            conditions.append(Tag.name == update_data['name'])
        if 'slug' in update_data:
            conditions.append(Tag.slug == update_data['slug'])
        
        duplicate_result = await db.execute(
            select(Tag).where(
                and_(
                    or_(*conditions),
                    Tag.id != tag_id
                )
            )
        )
        duplicate_tag = duplicate_result.scalar_one_or_none()
        
        if duplicate_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name or slug already exists"
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    await db.commit()
    await db.refresh(tag)
    
    return TagResponse.from_orm(tag)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    force: bool = Query(False, description="Force delete even if tag has events"),
    current_admin = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a tag (admin only)."""
    
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check if tag has events
    events_count_result = await db.execute(
        select(func.count(event_tags.c.event_id)).where(
            event_tags.c.tag_id == tag_id
        )
    )
    events_count = events_count_result.scalar()
    
    if events_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete tag with {events_count} events. Use force=true to delete anyway."
        )
    
    await db.delete(tag)
    await db.commit()
    
    return {"message": "Tag deleted successfully"}


@router.get("/suggest", response_model=List[TagResponse])
async def suggest_tags(
    query: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get tag suggestions based on partial name match."""
    
    search_term = f"%{query}%"
    
    # Get tags with event counts for better suggestions
    result = await db.execute(
        select(
            Tag,
            func.count(Event.id).label('event_count')
        ).outerjoin(
            event_tags, event_tags.c.tag_id == Tag.id
        ).outerjoin(
            Event,
            and_(
                Event.id == event_tags.c.event_id,
                Event.is_approved == True,
                Event.is_active == True
            )
        ).where(
            Tag.name.ilike(search_term)
        ).group_by(Tag.id).order_by(
            desc('event_count'),
            Tag.name
        ).limit(limit)
    )
    
    rows = result.all()
    
    tags = []
    for row in rows:
        tag_data = TagResponse.from_orm(row.Tag)
        tag_data.event_count = row.event_count
        tags.append(tag_data)
    
    return tags