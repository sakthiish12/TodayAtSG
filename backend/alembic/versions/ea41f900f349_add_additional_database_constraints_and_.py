"""Add additional database constraints and validation rules

Revision ID: ea41f900f349
Revises: e51ca43e8858
Create Date: 2025-07-29 22:15:03.373855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea41f900f349'
down_revision = 'e51ca43e8858'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add additional check constraints for data validation
    
    # 1. Event date validation - event should not be too far in the past or future
    op.execute("""
        CREATE TRIGGER validate_event_date
        BEFORE INSERT ON events
        WHEN NEW.date < date('now', '-1 year') OR NEW.date > date('now', '+5 years')
        BEGIN
            SELECT RAISE(ABORT, 'Event date must be within 1 year in the past and 5 years in the future');
        END;
    """)
    
    op.execute("""
        CREATE TRIGGER validate_event_date_update
        BEFORE UPDATE ON events
        WHEN NEW.date < date('now', '-1 year') OR NEW.date > date('now', '+5 years')
        BEGIN
            SELECT RAISE(ABORT, 'Event date must be within 1 year in the past and 5 years in the future');
        END;
    """)
    
    # 2. Latitude/Longitude validation for Singapore bounds
    # Singapore bounds: approx 1.2°N to 1.5°N, 103.6°E to 104.0°E
    op.execute("""
        CREATE TRIGGER validate_singapore_coords
        BEFORE INSERT ON events
        WHEN (NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL) AND
             (NEW.latitude < 1.0 OR NEW.latitude > 1.6 OR 
              NEW.longitude < 103.0 OR NEW.longitude > 104.5)
        BEGIN
            SELECT RAISE(ABORT, 'Coordinates must be within Singapore bounds');
        END;
    """)
    
    op.execute("""
        CREATE TRIGGER validate_singapore_coords_update
        BEFORE UPDATE ON events
        WHEN (NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL) AND
             (NEW.latitude < 1.0 OR NEW.latitude > 1.6 OR 
              NEW.longitude < 103.0 OR NEW.longitude > 104.5)
        BEGIN
            SELECT RAISE(ABORT, 'Coordinates must be within Singapore bounds');
        END;
    """)
    
    # 3. End date validation - end date should be >= start date
    op.execute("""
        CREATE TRIGGER validate_event_end_date
        BEFORE INSERT ON events
        WHEN NEW.end_date IS NOT NULL AND NEW.end_date < NEW.date
        BEGIN
            SELECT RAISE(ABORT, 'End date must be on or after start date');
        END;
    """)
    
    op.execute("""
        CREATE TRIGGER validate_event_end_date_update
        BEFORE UPDATE ON events
        WHEN NEW.end_date IS NOT NULL AND NEW.end_date < NEW.date
        BEGIN
            SELECT RAISE(ABORT, 'End date must be on or after start date');
        END;
    """)
    
    # 4. View count and click count validation
    op.execute("""
        CREATE TRIGGER validate_event_counts
        BEFORE INSERT ON events
        WHEN NEW.view_count < 0 OR NEW.click_count < 0
        BEGIN
            SELECT RAISE(ABORT, 'View count and click count must be non-negative');
        END;
    """)
    
    op.execute("""
        CREATE TRIGGER validate_event_counts_update
        BEFORE UPDATE ON events
        WHEN NEW.view_count < 0 OR NEW.click_count < 0
        BEGIN
            SELECT RAISE(ABORT, 'View count and click count must be non-negative');
        END;
    """)
    
    # 5. User preferred search radius validation
    op.execute("""
        CREATE TRIGGER validate_user_search_radius
        BEFORE INSERT ON users
        WHEN NEW.preferred_search_radius < 1 OR NEW.preferred_search_radius > 100
        BEGIN
            SELECT RAISE(ABORT, 'Preferred search radius must be between 1 and 100 km');
        END;
    """)
    
    op.execute("""
        CREATE TRIGGER validate_user_search_radius_update
        BEFORE UPDATE ON users
        WHEN NEW.preferred_search_radius < 1 OR NEW.preferred_search_radius > 100
        BEGIN
            SELECT RAISE(ABORT, 'Preferred search radius must be between 1 and 100 km');
        END;
    """)
    
    # 6. User login count validation
    op.execute("""
        CREATE TRIGGER validate_user_login_count
        BEFORE INSERT ON users
        WHEN NEW.login_count < 0
        BEGIN
            SELECT RAISE(ABORT, 'Login count must be non-negative');
        END;
    """)
    
    op.execute("""
        CREATE TRIGGER validate_user_login_count_update
        BEFORE UPDATE ON users
        WHEN NEW.login_count < 0
        BEGIN
            SELECT RAISE(ABORT, 'Login count must be non-negative');
        END;
    """)
    
    # 7. Email format validation (basic check)
    op.execute("""
        CREATE TRIGGER validate_user_email
        BEFORE INSERT ON users
        WHEN NEW.email NOT LIKE '%@%.%'
        BEGIN
            SELECT RAISE(ABORT, 'Invalid email format');
        END;
    """)
    
    op.execute("""
        CREATE TRIGGER validate_user_email_update
        BEFORE UPDATE ON users
        WHEN NEW.email NOT LIKE '%@%.%'
        BEGIN
            SELECT RAISE(ABORT, 'Invalid email format');
        END;
    """)


def downgrade() -> None:
    # Drop all triggers we created
    op.execute("DROP TRIGGER IF EXISTS validate_event_date")
    op.execute("DROP TRIGGER IF EXISTS validate_event_date_update")
    op.execute("DROP TRIGGER IF EXISTS validate_singapore_coords")
    op.execute("DROP TRIGGER IF EXISTS validate_singapore_coords_update")
    op.execute("DROP TRIGGER IF EXISTS validate_event_end_date")
    op.execute("DROP TRIGGER IF EXISTS validate_event_end_date_update")
    op.execute("DROP TRIGGER IF EXISTS validate_event_counts")
    op.execute("DROP TRIGGER IF EXISTS validate_event_counts_update")
    op.execute("DROP TRIGGER IF EXISTS validate_user_search_radius")
    op.execute("DROP TRIGGER IF EXISTS validate_user_search_radius_update")
    op.execute("DROP TRIGGER IF EXISTS validate_user_login_count")
    op.execute("DROP TRIGGER IF EXISTS validate_user_login_count_update")
    op.execute("DROP TRIGGER IF EXISTS validate_user_email")
    op.execute("DROP TRIGGER IF EXISTS validate_user_email_update")