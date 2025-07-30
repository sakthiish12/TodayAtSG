"""
Tests for events endpoints.
"""

import pytest
from httpx import AsyncClient
from datetime import date, time

from app.models.user import User
from app.models.category import Category
from app.models.event import Event


class TestEventEndpoints:
    """Test event endpoints."""
    
    async def test_get_events(self, client: AsyncClient):
        """Test getting events list."""
        response = await client.get("/api/events/")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert isinstance(data["events"], list)
    
    async def test_submit_event_authenticated(
        self,
        client: AsyncClient,
        test_user: User,
        test_category: Category,
        auth_headers_user: dict,
        sample_event_data: dict
    ):
        """Test event submission by authenticated user."""
        sample_event_data["category_id"] = test_category.id
        
        response = await client.post(
            "/api/events/submit", 
            json=sample_event_data, 
            headers=auth_headers_user
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_event_data["title"]
        assert data["is_approved"] == False  # User submissions need approval
        assert data["source"] == "user_submission"
    
    async def test_submit_event_unauthenticated(
        self, client: AsyncClient, sample_event_data: dict
    ):
        """Test event submission without authentication."""
        response = await client.post("/api/events/submit", json=sample_event_data)
        
        assert response.status_code == 401
    
    async def test_submit_event_invalid_data(
        self, client: AsyncClient, auth_headers_user: dict
    ):
        """Test event submission with invalid data."""
        invalid_data = {
            "title": "",  # Empty title
            "date": "invalid-date",
            "category_id": 9999  # Non-existent category
        }
        
        response = await client.post(
            "/api/events/submit", json=invalid_data, headers=auth_headers_user
        )
        
        assert response.status_code == 422
    
    async def test_create_event_organizer(
        self,
        client: AsyncClient,
        test_event_organizer: User,
        test_category: Category,
        auth_headers_organizer: dict,
        sample_event_data: dict
    ):
        """Test event creation by event organizer."""
        sample_event_data["category_id"] = test_category.id
        
        response = await client.post(
            "/api/events/", 
            json=sample_event_data, 
            headers=auth_headers_organizer
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_event_data["title"]
        assert data["source"] == "user_submission"
    
    async def test_create_event_admin_auto_approved(
        self,
        client: AsyncClient,
        test_admin_user: User,
        test_category: Category,
        auth_headers_admin: dict,
        sample_event_data: dict
    ):
        """Test event creation by admin (auto-approved)."""
        sample_event_data["category_id"] = test_category.id
        
        response = await client.post(
            "/api/events/", 
            json=sample_event_data, 
            headers=auth_headers_admin
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_approved"] == True  # Admin events auto-approved
    
    async def test_get_single_event(
        self,
        client: AsyncClient,
        db_session,
        test_category: Category,
        test_admin_user: User
    ):
        """Test getting a single event."""
        # Create a test event
        event = Event(
            title="Test Single Event",
            description="Test description",
            date=date(2024, 12, 25),
            time=time(19, 0),
            location="Singapore",
            category_id=test_category.id,
            submitted_by_id=test_admin_user.id,
            source="admin",
            is_approved=True,
            is_active=True
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        response = await client.get(f"/api/events/{event.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event.id
        assert data["title"] == event.title
        assert "category" in data
    
    async def test_get_nonexistent_event(self, client: AsyncClient):
        """Test getting non-existent event."""
        response = await client.get("/api/events/99999")
        
        assert response.status_code == 404
    
    async def test_update_own_event(
        self,
        client: AsyncClient,
        db_session,
        test_category: Category,
        test_user: User,
        auth_headers_user: dict
    ):
        """Test updating user's own event."""
        # Create an event owned by test_user
        event = Event(
            title="Original Title",
            description="Original description",
            date=date(2024, 12, 25),
            time=time(19, 0),
            location="Singapore",
            category_id=test_category.id,
            submitted_by_id=test_user.id,
            source="user_submission",
            is_approved=False,
            is_active=True
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        
        response = await client.put(
            f"/api/events/{event.id}", 
            json=update_data, 
            headers=auth_headers_user
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
    
    async def test_update_other_user_event_forbidden(
        self,
        client: AsyncClient,
        db_session,
        test_category: Category,
        test_user: User,
        test_admin_user: User,
        auth_headers_user: dict
    ):
        """Test updating another user's event (should be forbidden)."""
        # Create an event owned by admin
        event = Event(
            title="Admin Event",
            description="Admin description",
            date=date(2024, 12, 25),
            time=time(19, 0),
            location="Singapore",
            category_id=test_category.id,
            submitted_by_id=test_admin_user.id,
            source="admin",
            is_approved=True,
            is_active=True
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        update_data = {"title": "Hacked Title"}
        
        response = await client.put(
            f"/api/events/{event.id}", 
            json=update_data, 
            headers=auth_headers_user
        )
        
        assert response.status_code == 403
    
    async def test_delete_own_event(
        self,
        client: AsyncClient,
        db_session,
        test_category: Category,
        test_user: User,
        auth_headers_user: dict
    ):
        """Test deleting user's own event."""
        # Create an event owned by test_user
        event = Event(
            title="Event to Delete",
            description="Will be deleted",
            date=date(2024, 12, 25),
            time=time(19, 0),
            location="Singapore",
            category_id=test_category.id,
            submitted_by_id=test_user.id,
            source="user_submission",
            is_approved=False,
            is_active=True
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        response = await client.delete(f"/api/events/{event.id}", headers=auth_headers_user)
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
    
    async def test_search_events_with_filters(self, client: AsyncClient):
        """Test event search with filters."""
        search_data = {
            "search": "test",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "is_upcoming": True,
            "skip": 0,
            "limit": 10
        }
        
        response = await client.post("/api/events/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert "filters_applied" in data
    
    async def test_get_nearby_events(self, client: AsyncClient):
        """Test getting nearby events."""
        # Singapore coordinates
        params = {
            "latitude": 1.3521,
            "longitude": 103.8198,
            "radius_km": 10,
            "limit": 20
        }
        
        response = await client.get("/api/events/nearby", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "search_center" in data
    
    async def test_get_featured_events(self, client: AsyncClient):
        """Test getting featured events."""
        response = await client.get("/api/events/featured")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert isinstance(data["events"], list)
    
    async def test_track_event_click(
        self,
        client: AsyncClient,
        db_session,
        test_category: Category,
        test_admin_user: User
    ):
        """Test tracking event click."""
        # Create a test event
        event = Event(
            title="Clickable Event",
            description="Test click tracking",
            date=date(2024, 12, 25),
            time=time(19, 0),
            location="Singapore",
            category_id=test_category.id,
            submitted_by_id=test_admin_user.id,
            source="admin",
            is_approved=True,
            is_active=True
        )
        db_session.add(event)
        await db_session.commit()
        await db_session.refresh(event)
        
        initial_click_count = event.click_count
        
        response = await client.post(f"/api/events/{event.id}/click")
        
        assert response.status_code == 200
        assert "tracked successfully" in response.json()["message"]