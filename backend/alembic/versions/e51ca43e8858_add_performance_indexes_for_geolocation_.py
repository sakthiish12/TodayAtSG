"""Add performance indexes for geolocation and search optimization

Revision ID: e51ca43e8858
Revises: 31f73fc9046f
Create Date: 2025-07-29 22:13:53.124012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e51ca43e8858'
down_revision = '31f73fc9046f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Composite indexes for events table - optimized for common queries
    
    # 1. Geolocation search optimization - for "near me" queries
    op.create_index(
        'idx_events_location_coords',
        'events',
        ['latitude', 'longitude', 'is_approved', 'is_active'],
        unique=False
    )
    
    # 2. Date-based search optimization - for upcoming events
    op.create_index(
        'idx_events_date_approved_active',
        'events',
        ['date', 'is_approved', 'is_active'],
        unique=False
    )
    
    # 3. Category-based search with date filtering
    op.create_index(
        'idx_events_category_date_approved',
        'events',
        ['category_id', 'date', 'is_approved', 'is_active'],
        unique=False
    )
    
    # 4. Source-based filtering (for admin/scraped content management)
    op.create_index(
        'idx_events_source_created',
        'events',
        ['source', 'created_at', 'is_approved'],
        unique=False
    )
    
    # 5. Location-based text search optimization
    op.create_index(
        'idx_events_location_date',
        'events',
        ['location', 'date', 'is_approved'],
        unique=False
    )
    
    # 6. Featured events optimization
    op.create_index(
        'idx_events_featured_date',
        'events',
        ['is_featured', 'date', 'is_approved', 'is_active'],
        unique=False
    )
    
    # 7. User submissions optimization
    op.create_index(
        'idx_events_submitted_by_date',
        'events',
        ['submitted_by_id', 'created_at', 'is_approved'],
        unique=False
    )
    
    # 8. Analytics optimization - for popular events
    op.create_index(
        'idx_events_view_count_date',
        'events',
        ['view_count', 'date', 'is_approved'],
        unique=False
    )
    
    # 9. Scraped content tracking
    op.create_index(
        'idx_events_scraped_from_updated',
        'events',
        ['scraped_from', 'last_scraped', 'is_active'],
        unique=False
    )
    
    # Reviews table optimization
    
    # 10. Event reviews aggregation
    op.create_index(
        'idx_reviews_event_rating_created',
        'reviews',
        ['event_id', 'rating', 'created_at'],
        unique=False
    )
    
    # 11. User reviews tracking
    op.create_index(
        'idx_reviews_user_created',
        'reviews',
        ['user_id', 'created_at'],
        unique=False
    )
    
    # 12. Verified reviews prioritization
    op.create_index(
        'idx_reviews_verified_rating',
        'reviews',
        ['is_verified', 'rating', 'created_at'],
        unique=False
    )
    
    # Users table optimization
    
    # 13. Event organizer filtering
    op.create_index(
        'idx_users_organizer_active',
        'users',
        ['is_event_organizer', 'is_active', 'is_verified'],
        unique=False
    )
    
    # 14. Admin user filtering
    op.create_index(
        'idx_users_admin_active',
        'users',
        ['is_admin', 'is_active'],
        unique=False
    )
    
    # 15. User location preferences (for personalized recommendations)
    op.create_index(
        'idx_users_location_prefs',
        'users',
        ['preferred_location_lat', 'preferred_location_lng', 'is_active'],
        unique=False
    )
    
    # Tags table optimization
    
    # 16. Popular tags tracking (for event_tags association table)
    # Note: SQLite doesn't support partial indexes, but we can create regular ones
    op.create_index(
        'idx_event_tags_tag_event',
        'event_tags',
        ['tag_id', 'event_id'],
        unique=False
    )
    
    # Categories table optimization (already well-indexed from initial migration)
    
    # 17. Category sorting optimization
    op.create_index(
        'idx_categories_sort_name',
        'categories',
        ['sort_order', 'name'],
        unique=False
    )


def downgrade() -> None:
    # Drop all the custom indexes we created
    op.drop_index('idx_categories_sort_name', table_name='categories')
    op.drop_index('idx_event_tags_tag_event', table_name='event_tags')
    op.drop_index('idx_users_location_prefs', table_name='users')
    op.drop_index('idx_users_admin_active', table_name='users')
    op.drop_index('idx_users_organizer_active', table_name='users')
    op.drop_index('idx_reviews_verified_rating', table_name='reviews')
    op.drop_index('idx_reviews_user_created', table_name='reviews')
    op.drop_index('idx_reviews_event_rating_created', table_name='reviews')
    op.drop_index('idx_events_scraped_from_updated', table_name='events')
    op.drop_index('idx_events_view_count_date', table_name='events')
    op.drop_index('idx_events_submitted_by_date', table_name='events')
    op.drop_index('idx_events_featured_date', table_name='events')
    op.drop_index('idx_events_location_date', table_name='events')
    op.drop_index('idx_events_source_created', table_name='events')
    op.drop_index('idx_events_category_date_approved', table_name='events')
    op.drop_index('idx_events_date_approved_active', table_name='events')
    op.drop_index('idx_events_location_coords', table_name='events')