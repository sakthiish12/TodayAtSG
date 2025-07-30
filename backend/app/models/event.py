from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, Boolean, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

from app.db.database import Base
from app.models.event_tag import event_tags


class Event(Base):
    """Event model for storing event information."""
    
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    # Date and time
    date = Column(Date, nullable=False, index=True)
    time = Column(Time, nullable=False)
    end_date = Column(Date, nullable=True)
    end_time = Column(Time, nullable=True)
    
    # Location
    location = Column(String(255), nullable=False, index=True)
    venue = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True, index=True)
    longitude = Column(Numeric(11, 8), nullable=True, index=True)
    
    # Event details
    age_restrictions = Column(String(50), nullable=True)
    price_info = Column(String(200), nullable=True)
    external_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Categorization
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False, index=True)
    
    # Status and metadata
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    source = Column(String(100), nullable=False, default='user_submission', index=True)  # 'user_submission', 'scraped', 'admin'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # User who submitted (for user submissions)
    submitted_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Scraped data metadata
    scraped_from = Column(String(100), nullable=True)  # Source website
    external_id = Column(String(100), nullable=True)  # External event ID
    last_scraped = Column(DateTime(timezone=True), nullable=True)
    
    # Analytics
    view_count = Column(Integer, default=0, nullable=False)
    click_count = Column(Integer, default=0, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="events")
    tags = relationship("Tag", secondary=event_tags, back_populates="events")
    reviews = relationship("Review", back_populates="event", cascade="all, delete-orphan")
    submitted_by = relationship("User", back_populates="submitted_events", foreign_keys=[submitted_by_id])

    @hybrid_property
    def average_rating(self):
        """Calculate average rating from reviews."""
        if self.reviews:
            return sum(review.rating for review in self.reviews) / len(self.reviews)
        return None

    @hybrid_property
    def review_count(self):
        """Get total number of reviews."""
        return len(self.reviews) if self.reviews else 0

    @hybrid_property
    def is_upcoming(self):
        """Check if event is in the future."""
        event_datetime = datetime.combine(self.date, self.time)
        return event_datetime > datetime.now()

    @hybrid_property
    def is_past(self):
        """Check if event has already happened."""
        return not self.is_upcoming

    @hybrid_property
    def datetime(self):
        """Get combined datetime object."""
        return datetime.combine(self.date, self.time)

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', date='{self.date}', approved={self.is_approved})>"