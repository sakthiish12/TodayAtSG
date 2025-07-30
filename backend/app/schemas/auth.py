from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_event_organizer: Optional[bool] = False


class UserCreate(UserBase):
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        from app.core.security import validate_password
        is_valid, message = validate_password(v)
        if not is_valid:
            raise ValueError(message)
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_location_lat: Optional[str] = None
    preferred_location_lng: Optional[str] = None
    preferred_search_radius: Optional[int] = None
    
    @validator('preferred_search_radius')
    def validate_search_radius(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError('Search radius must be between 1 and 100 km')
        return v


class UserResponse(UserBase):
    id: int
    full_name: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    preferred_search_radius: int
    last_login: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        from app.core.security import validate_password
        is_valid, message = validate_password(v)
        if not is_valid:
            raise ValueError(message)
        return v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        from app.core.security import validate_password
        is_valid, message = validate_password(v)
        if not is_valid:
            raise ValueError(message)
        return v


class TokenData(BaseModel):
    user_id: Optional[int] = None
