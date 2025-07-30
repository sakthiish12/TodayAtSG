from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v
    
    @validator('comment')
    def validate_comment(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError('Comment must be less than 1000 characters')
            if len(v) < 10:
                raise ValueError('Comment must be at least 10 characters long')
        return v


class ReviewCreate(ReviewBase):
    event_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v
    
    @validator('comment')
    def validate_comment(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError('Comment must be less than 1000 characters')
            if len(v) < 10:
                raise ValueError('Comment must be at least 10 characters long')
        return v


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    event_id: int
    user_name: str  # Computed from user relationship
    is_verified: bool
    is_reported: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    reviews: list[ReviewResponse]
    total: int
    skip: int
    limit: int
    average_rating: Optional[float] = None


class ReviewReport(BaseModel):
    reason: str
    description: Optional[str] = None
    
    @validator('reason')
    def validate_reason(cls, v):
        valid_reasons = [
            'inappropriate_content',
            'spam',
            'fake_review',
            'harassment',
            'offensive_language',
            'other'
        ]
        if v not in valid_reasons:
            raise ValueError(f'Invalid reason. Must be one of: {", ".join(valid_reasons)}')
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Description must be less than 500 characters')
        return v


class ReviewStats(BaseModel):
    total_reviews: int
    average_rating: Optional[float] = None
    rating_distribution: dict[int, int]  # {1: count, 2: count, ...}
    recent_reviews: list[ReviewResponse]