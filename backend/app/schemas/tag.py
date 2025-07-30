from pydantic import BaseModel, validator
from typing import Optional


class TagBase(BaseModel):
    name: str
    slug: str
    color: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Tag name must be at least 2 characters long')
        if len(v) > 50:
            raise ValueError('Tag name must be less than 50 characters')
        return v.strip()
    
    @validator('slug')
    def validate_slug(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Tag slug must be at least 2 characters long')
        if len(v) > 50:
            raise ValueError('Tag slug must be less than 50 characters')
        # Simple slug validation (alphanumeric and hyphens)
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Tag slug must contain only alphanumeric characters, hyphens, and underscores')
        return v.strip().lower()
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            # Validate hex color format
            if not v.startswith('#') or len(v) != 7:
                raise ValueError('Color must be a valid hex color code (e.g., #FF0000)')
            try:
                int(v[1:], 16)  # Validate hex characters
            except ValueError:
                raise ValueError('Color must be a valid hex color code')
        return v


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    color: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Tag name must be at least 2 characters long')
            if len(v) > 50:
                raise ValueError('Tag name must be less than 50 characters')
            return v.strip()
        return v
    
    @validator('slug')
    def validate_slug(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Tag slug must be at least 2 characters long')
            if len(v) > 50:
                raise ValueError('Tag slug must be less than 50 characters')
            # Simple slug validation (alphanumeric and hyphens)
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Tag slug must contain only alphanumeric characters, hyphens, and underscores')
            return v.strip().lower()
        return v
    
    @validator('color')
    def validate_color(cls, v):
        if v is not None:
            # Validate hex color format
            if not v.startswith('#') or len(v) != 7:
                raise ValueError('Color must be a valid hex color code (e.g., #FF0000)')
            try:
                int(v[1:], 16)  # Validate hex characters
            except ValueError:
                raise ValueError('Color must be a valid hex color code')
        return v


class TagResponse(TagBase):
    id: int
    event_count: Optional[int] = None  # Optional event count when requested
    
    class Config:
        from_attributes = True