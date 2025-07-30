from sqlalchemy import Column, Integer, ForeignKey, Table

from app.db.database import Base

# Association table for many-to-many relationship between events and tags
event_tags = Table(
    'event_tags',
    Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)