#!/usr/bin/env python3
"""
TodayAtSG Database Management Script

This script provides easy-to-use commands for managing the TodayAtSG database,
including migrations, seeding, and testing.

Usage:
    python manage.py [command] [options]

Commands:
    init-db        Initialize database with migrations and seed data
    migrate        Run database migrations
    seed           Seed database with sample data
    reset-db       Reset database (drop all tables and recreate)
    test-db        Test database connections and operations
    create-admin   Create an admin user
    backup         Backup database (SQLite only)
    restore        Restore database from backup (SQLite only)

Examples:
    python manage.py init-db
    python manage.py migrate
    python manage.py seed
    python manage.py reset-db --confirm
    python manage.py create-admin --email admin@example.com --password mypassword
"""

import asyncio
import sys
import argparse
import os
from pathlib import Path
from datetime import datetime

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.database import Base, AsyncSessionLocal
from app.core.config import settings
from app.core.security import get_password_hash


class DatabaseManager:
    """Database management utilities."""
    
    def __init__(self):
        self.sync_engine = create_engine(settings.DATABASE_URL_SYNC)
        self.async_engine = create_async_engine(settings.DATABASE_URL)
        self.async_session = async_sessionmaker(self.async_engine, class_=AsyncSession)

    async def init_database(self):
        """Initialize database with migrations and seed data."""
        print("🚀 Initializing TodayAtSG database...")
        
        # Run migrations
        print("📦 Running database migrations...")
        os.system("alembic upgrade head")
        
        # Seed database
        print("🌱 Seeding database with sample data...")
        await self.seed_database()
        
        print("✅ Database initialization completed!")

    async def migrate_database(self):
        """Run database migrations."""
        print("📦 Running database migrations...")
        os.system("alembic upgrade head")
        print("✅ Migrations completed!")

    async def seed_database(self):
        """Seed database with sample data."""
        print("🌱 Seeding database...")
        
        async with self.async_session() as db:
            try:
                # Import models to ensure they're loaded
                from app.models.user import User
                from app.models.category import Category
                from app.models.tag import Tag
                from app.models.event import Event
                from app.models.review import Review
                
                # Seed categories
                await self._seed_categories(db)
                
                # Seed tags
                await self._seed_tags(db)
                
                # Seed admin user
                await self._seed_admin_user(db)
                
                # Seed sample events (simplified)
                await self._seed_sample_events(db)
                
                print("✅ Database seeding completed!")
                
            except Exception as e:
                print(f"❌ Error during seeding: {str(e)}")
                await db.rollback()
                raise

    async def _seed_categories(self, db: AsyncSession):
        """Seed categories."""
        from app.models.category import Category
        from sqlalchemy import select
        
        categories_data = [
            {"name": "Concerts", "slug": "concerts", "description": "Live music performances", "icon": "🎵", "color": "#FF6B6B", "sort_order": 1},
            {"name": "Festivals", "slug": "festivals", "description": "Cultural festivals and celebrations", "icon": "🎉", "color": "#4ECDC4", "sort_order": 2},
            {"name": "DJ Events", "slug": "dj-events", "description": "Electronic music and DJ sets", "icon": "🎧", "color": "#45B7D1", "sort_order": 3},
            {"name": "Kids Events", "slug": "kids-events", "description": "Family-friendly activities", "icon": "🧸", "color": "#96CEB4", "sort_order": 4},
            {"name": "Food & Drink", "slug": "food-drink", "description": "Culinary experiences", "icon": "🍽️", "color": "#FECA57", "sort_order": 5},
            {"name": "Art & Culture", "slug": "art-culture", "description": "Art exhibitions and cultural shows", "icon": "🎨", "color": "#FF9FF3", "sort_order": 6},
            {"name": "Sports & Fitness", "slug": "sports-fitness", "description": "Sports events and fitness activities", "icon": "⚽", "color": "#54A0FF", "sort_order": 7},
            {"name": "Workshops", "slug": "workshops", "description": "Educational workshops and classes", "icon": "📚", "color": "#5F27CD", "sort_order": 8},
            {"name": "Nightlife", "slug": "nightlife", "description": "Bars, clubs, and nighttime entertainment", "icon": "🌙", "color": "#222f3e", "sort_order": 9},
            {"name": "Networking", "slug": "networking", "description": "Business networking and professional events", "icon": "🤝", "color": "#10ac84", "sort_order": 10}
        ]
        
        for category_data in categories_data:
            result = await db.execute(select(Category).where(Category.slug == category_data["slug"]))
            existing = result.scalar_one_or_none()
            
            if not existing:
                category = Category(**category_data)
                db.add(category)
                print(f"  Added category: {category_data['name']}")
        
        await db.commit()

    async def _seed_tags(self, db: AsyncSession):
        """Seed tags."""
        from app.models.tag import Tag
        from sqlalchemy import select
        
        tags_data = [
            {"name": "Outdoor", "slug": "outdoor", "color": "#2ecc71"},
            {"name": "Indoor", "slug": "indoor", "color": "#3498db"},
            {"name": "Free", "slug": "free", "color": "#27ae60"},
            {"name": "Paid", "slug": "paid", "color": "#e74c3c"},
            {"name": "Family Friendly", "slug": "family-friendly", "color": "#f39c12"},
            {"name": "Adults Only", "slug": "adults-only", "color": "#8e44ad"},
            {"name": "Weekend", "slug": "weekend", "color": "#16a085"},
            {"name": "Weekday", "slug": "weekday", "color": "#2980b9"},
            {"name": "Marina Bay", "slug": "marina-bay", "color": "#d35400"},
            {"name": "Orchard", "slug": "orchard", "color": "#c0392b"},
            {"name": "Clarke Quay", "slug": "clarke-quay", "color": "#9b59b6"},
            {"name": "Sentosa", "slug": "sentosa", "color": "#1abc9c"},
            {"name": "Chinatown", "slug": "chinatown", "color": "#e67e22"},
            {"name": "Little India", "slug": "little-india", "color": "#f1c40f"},
            {"name": "Bugis", "slug": "bugis", "color": "#34495e"}
        ]
        
        for tag_data in tags_data:
            result = await db.execute(select(Tag).where(Tag.slug == tag_data["slug"]))
            existing = result.scalar_one_or_none()
            
            if not existing:
                tag = Tag(**tag_data)
                db.add(tag)
                print(f"  Added tag: {tag_data['name']}")
        
        await db.commit()

    async def _seed_admin_user(self, db: AsyncSession):
        """Create admin user."""
        from app.models.user import User
        from sqlalchemy import select
        
        admin_email = "admin@todayatsg.com"
        
        result = await db.execute(select(User).where(User.email == admin_email))
        existing_admin = result.scalar_one_or_none()
        
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                password_hash=get_password_hash("admin123!@#"),
                first_name="System",
                last_name="Administrator",
                is_admin=True,
                is_event_organizer=True,
                is_active=True,
                is_verified=True
            )
            
            db.add(admin_user)
            await db.commit()
            print(f"  Created admin user: {admin_email}")
            print("  ⚠️  WARNING: Change the default admin password in production!")
        else:
            print("  Admin user already exists")

    async def _seed_sample_events(self, db: AsyncSession):
        """Seed a few basic sample events."""
        print("  Adding sample events (basic set)...")
        # For now, just confirm the structure works
        # Full event seeding can be added later when async issues are resolved
        print("  Sample events seeding deferred - database structure ready")

    async def reset_database(self, confirm=False):
        """Reset database by dropping and recreating all tables."""
        if not confirm:
            print("⚠️  WARNING: This will delete ALL data in the database!")
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Operation cancelled.")
                return
        
        print("🗑️  Dropping all tables...")
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database reset completed!")
        
        # Re-seed with basic data
        await self.seed_database()

    async def test_database(self):
        """Test database connections and basic operations."""
        print("🧪 Testing database connections...")
        
        try:
            # Test async connection
            async with self.async_engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
            print("✅ Async database connection: OK")
            
            # Test sync connection
            with self.sync_engine.begin() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
            print("✅ Sync database connection: OK")
            
            # Test table existence
            async with self.async_engine.begin() as conn:
                result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]
                
                expected_tables = ['users', 'categories', 'tags', 'events', 'reviews', 'event_tags']
                for table in expected_tables:
                    if table in tables:
                        print(f"✅ Table '{table}': EXISTS")
                    else:
                        print(f"❌ Table '{table}': MISSING")
            
            print("✅ Database tests completed!")
            
        except Exception as e:
            print(f"❌ Database test failed: {str(e)}")
            raise

    async def create_admin_user(self, email: str, password: str):
        """Create a new admin user."""
        from app.models.user import User
        from sqlalchemy import select
        
        async with self.async_session() as db:
            # Check if user already exists
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ User with email {email} already exists!")
                return
            
            # Create new admin user
            admin_user = User(
                email=email,
                password_hash=get_password_hash(password),
                first_name="Admin",
                last_name="User",
                is_admin=True,
                is_event_organizer=True,
                is_active=True,
                is_verified=True
            )
            
            db.add(admin_user)
            await db.commit()
            print(f"✅ Created admin user: {email}")

    def backup_database(self, backup_path: str = None):
        """Backup SQLite database."""
        if not settings.DATABASE_URL_SYNC.startswith("sqlite"):
            print("❌ Backup only supported for SQLite databases")
            return
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_todayatsg_{timestamp}.db"
        
        db_path = settings.DATABASE_URL_SYNC.replace("sqlite:///", "")
        
        import shutil
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
        except Exception as e:
            print(f"❌ Backup failed: {str(e)}")

    def restore_database(self, backup_path: str):
        """Restore SQLite database from backup."""
        if not settings.DATABASE_URL_SYNC.startswith("sqlite"):
            print("❌ Restore only supported for SQLite databases")
            return
        
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return
        
        db_path = settings.DATABASE_URL_SYNC.replace("sqlite:///", "")
        
        import shutil
        try:
            shutil.copy2(backup_path, db_path)
            print(f"✅ Database restored from: {backup_path}")
        except Exception as e:
            print(f"❌ Restore failed: {str(e)}")


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="TodayAtSG Database Management")
    parser.add_argument("command", choices=[
        "init-db", "migrate", "seed", "reset-db", "test-db", 
        "create-admin", "backup", "restore"
    ])
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive operations")
    parser.add_argument("--email", help="Email for admin user creation")
    parser.add_argument("--password", help="Password for admin user creation")
    parser.add_argument("--backup-path", help="Backup file path")
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager()
    
    try:
        if args.command == "init-db":
            await db_manager.init_database()
        elif args.command == "migrate":
            await db_manager.migrate_database()
        elif args.command == "seed":
            await db_manager.seed_database()
        elif args.command == "reset-db":
            await db_manager.reset_database(confirm=args.confirm)
        elif args.command == "test-db":
            await db_manager.test_database()
        elif args.command == "create-admin":
            if not args.email or not args.password:
                print("❌ Email and password required for admin creation")
                print("Usage: python manage.py create-admin --email admin@example.com --password mypassword")
                sys.exit(1)
            await db_manager.create_admin_user(args.email, args.password)
        elif args.command == "backup":
            db_manager.backup_database(args.backup_path)
        elif args.command == "restore":
            if not args.backup_path:
                print("❌ Backup path required for restore")
                print("Usage: python manage.py restore --backup-path backup_file.db")
                sys.exit(1)
            db_manager.restore_database(args.backup_path)
            
    except Exception as e:
        print(f"❌ Command failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())