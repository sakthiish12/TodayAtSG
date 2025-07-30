from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class Review(Base):
    """Review model for event ratings and comments."""
    
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    rating = Column(Integer, nullable=False, index=True)
    comment = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)  # For verified attendees
    is_reported = Column(Boolean, default=False, nullable=False)
    report_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="reviews")
    event = relationship("Event", back_populates="reviews")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='unique_user_event_review'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range_check'),
        CheckConstraint('report_count >= 0', name='report_count_positive'),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, event_id={self.event_id}, rating={self.rating})>"