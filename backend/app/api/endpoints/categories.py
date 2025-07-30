from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Optional
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.core.security import get_current_admin_user, get_current_user
from app.models.category import Category
from app.models.event import Event
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    include_event_count: bool = Query(False),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all categories with optional event counts."""
    
    if include_event_count:
        # Query with event count
        query = select(
            Category,
            func.count(Event.id).label('event_count')
        ).outerjoin(
            Event, 
            and_(
                Event.category_id == Category.id,
                Event.is_approved == True,
                Event.is_active == True
            )
        ).group_by(Category.id).order_by(Category.sort_order, Category.name)
        
        result = await db.execute(query)
        rows = result.all()
        
        categories = []
        for row in rows:
            category_data = CategoryResponse.from_orm(row.Category)
            category_data.event_count = row.event_count
            categories.append(category_data)
        
        return categories
    else:
        # Simple query without event count
        result = await db.execute(
            select(Category).order_by(Category.sort_order, Category.name)
        )
        categories = result.scalars().all()
        
        return [CategoryResponse.from_orm(category) for category in categories]


@router.get("/popular", response_model=List[CategoryResponse])
async def get_popular_categories(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get categories ordered by number of events."""
    
    query = select(
        Category,
        func.count(Event.id).label('event_count')
    ).outerjoin(
        Event,
        and_(
            Event.category_id == Category.id,
            Event.is_approved == True,
            Event.is_active == True
        )
    ).group_by(Category.id).order_by(
        desc('event_count'),
        Category.name
    ).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    categories = []
    for row in rows:
        category_data = CategoryResponse.from_orm(row.Category)
        category_data.event_count = row.event_count
        categories.append(category_data)
    
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    include_event_count: bool = Query(False),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get a specific category by ID."""
    
    if include_event_count:
        query = select(
            Category,
            func.count(Event.id).label('event_count')
        ).outerjoin(
            Event,
            and_(
                Event.category_id == Category.id,
                Event.is_approved == True,
                Event.is_active == True
            )
        ).where(Category.id == category_id).group_by(Category.id)
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        category_data = CategoryResponse.from_orm(row.Category)
        category_data.event_count = row.event_count
        
        return category_data
    else:
        result = await db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return CategoryResponse.from_orm(category)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_admin = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new category (admin only)."""
    
    # Check if category already exists
    result = await db.execute(
        select(Category).where(
            or_(
                Category.name == category_data.name,
                Category.slug == category_data.slug
            )
        )
    )
    existing_category = result.scalar_one_or_none()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name or slug already exists"
        )
    
    category = Category(**category_data.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.from_orm(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_admin = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update an existing category (admin only)."""
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check for duplicate name/slug if being updated
    update_data = category_data.dict(exclude_unset=True)
    if 'name' in update_data or 'slug' in update_data:
        conditions = []
        if 'name' in update_data:
            conditions.append(Category.name == update_data['name'])
        if 'slug' in update_data:
            conditions.append(Category.slug == update_data['slug'])
        
        duplicate_result = await db.execute(
            select(Category).where(
                and_(
                    or_(*conditions),
                    Category.id != category_id
                )
            )
        )
        duplicate_category = duplicate_result.scalar_one_or_none()
        
        if duplicate_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name or slug already exists"
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.from_orm(category)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    force: bool = Query(False, description="Force delete even if category has events"),
    current_admin = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Delete a category (admin only)."""
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if category has events
    events_count_result = await db.execute(
        select(func.count(Event.id)).where(Event.category_id == category_id)
    )
    events_count = events_count_result.scalar()
    
    if events_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {events_count} events. Use force=true to delete anyway."
        )
    
    await db.delete(category)
    await db.commit()
    
    return {"message": "Category deleted successfully"}