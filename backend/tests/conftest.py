"""
Test configuration and fixtures for TodayAtSG backend tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db, Base
from app.core.config import settings
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.core.security import get_password_hash

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database dependency override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_category(db_session: AsyncSession) -> Category:
    """Create a test category."""
    category = Category(
        name="Test Festivals",
        slug="test-festivals",
        description="Test festival category",
        icon="🎉",
        color="#FF6B6B",
        sort_order=1
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_tag(db_session: AsyncSession) -> Tag:
    """Create a test tag."""
    tag = Tag(
        name="Test Tag",
        slug="test-tag",
        color="#FF6B6B"
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)
    return tag


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_verified=True,
        is_admin=True,
        is_event_organizer=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
async def test_event_organizer(db_session: AsyncSession) -> User:
    """Create a test event organizer user."""
    organizer = User(
        email="organizer@example.com",
        password_hash=get_password_hash("organizerpassword123"),
        first_name="Event",
        last_name="Organizer",
        is_active=True,
        is_verified=True,
        is_event_organizer=True
    )
    db_session.add(organizer)
    await db_session.commit()
    await db_session.refresh(organizer)
    return organizer


@pytest.fixture
def auth_headers_user(test_user: User) -> dict:
    """Create authorization headers for test user."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_admin(test_admin_user: User) -> dict:
    """Create authorization headers for admin user."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(
        data={"sub": str(test_admin_user.id), "email": test_admin_user.email}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_organizer(test_event_organizer: User) -> dict:
    """Create authorization headers for event organizer."""
    from app.core.security import create_access_token
    
    access_token = create_access_token(
        data={"sub": str(test_event_organizer.id), "email": test_event_organizer.email}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "title": "Test Event",
        "description": "This is a test event description",
        "short_description": "Test event",
        "date": "2024-12-25",
        "time": "19:00:00",
        "location": "Singapore",
        "venue": "Test Venue",
        "address": "123 Test Street, Singapore 123456",
        "latitude": 1.3521,
        "longitude": 103.8198,
        "age_restrictions": "All ages welcome",
        "price_info": "Free",
        "external_url": "https://example.com/event"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "newuser@example.com",
        "password": "NewPassword123!",
        "confirm_password": "NewPassword123!",
        "first_name": "New",
        "last_name": "User",
        "phone_number": "+6591234567"
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing."""
    return {
        "rating": 5,
        "comment": "This was an amazing event! Highly recommended for everyone."
    }