from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """User model for authentication and event management."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # User details
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # User roles and status
    is_event_organizer = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Authentication tokens
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # User preferences
    preferred_location_lat = Column(String(20), nullable=True)  # User's preferred location
    preferred_location_lng = Column(String(20), nullable=True)
    preferred_search_radius = Column(Integer, default=10, nullable=False)  # in km
    
    # Account metadata
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    submitted_events = relationship("Event", back_populates="submitted_by", foreign_keys="Event.submitted_by_id")

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.email.split('@')[0]  # Fallback to email username
    
    @property
    def is_super_admin(self) -> bool:
        """Check if user is a super admin."""
        from app.core.config import settings
        return self.is_admin and self.email == settings.SUPER_ADMIN_EMAIL
    
    def can_submit_free_event(self) -> bool:
        """Check if user can submit a free event this month."""
        # This would need to check against event submissions in current month
        # For now, return True if they're an event organizer
        return self.is_event_organizer
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', is_organizer={self.is_event_organizer}, is_admin={self.is_admin})>"