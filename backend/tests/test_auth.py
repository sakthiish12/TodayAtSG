"""
Tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    async def test_register_user(self, client: AsyncClient, sample_user_data: dict):
        """Test user registration."""
        response = await client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert "id" in data
    
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user: User, sample_user_data: dict
    ):
        """Test registration with duplicate email."""
        sample_user_data["email"] = test_user.email
        
        response = await client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    async def test_register_invalid_password(self, client: AsyncClient):
        """Test registration with invalid password."""
        user_data = {
            "email": "test@example.com",
            "password": "weak",  # Too weak
            "confirm_password": "weak",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    async def test_register_password_mismatch(self, client: AsyncClient):
        """Test registration with password mismatch."""
        user_data = {
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "confirm_password": "DifferentPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422
        assert "do not match" in str(response.json())
    
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = await client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email
    
    async def test_login_invalid_credentials(self, client: AsyncClient, test_user: User):
        """Test login with invalid credentials."""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 401
    
    async def test_get_current_user(
        self, client: AsyncClient, test_user: User, auth_headers_user: dict
    ):
        """Test getting current user info."""
        response = await client.get("/api/auth/me", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    async def test_update_current_user(
        self, client: AsyncClient, test_user: User, auth_headers_user: dict
    ):
        """Test updating current user info."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "+6591234567"
        }
        
        response = await client.put(
            "/api/auth/me", json=update_data, headers=auth_headers_user
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
    
    async def test_change_password(
        self, client: AsyncClient, test_user: User, auth_headers_user: dict
    ):
        """Test changing password."""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        
        response = await client.post(
            "/api/auth/change-password", json=password_data, headers=auth_headers_user
        )
        
        assert response.status_code == 200
        assert "successfully" in response.json()["message"]
    
    async def test_change_password_wrong_current(
        self, client: AsyncClient, test_user: User, auth_headers_user: dict
    ):
        """Test changing password with wrong current password."""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
        
        response = await client.post(
            "/api/auth/change-password", json=password_data, headers=auth_headers_user
        )
        
        assert response.status_code == 400
        assert "Incorrect current password" in response.json()["detail"]
    
    async def test_refresh_token(self, client: AsyncClient, test_user: User):
        """Test token refresh."""
        # First login to get tokens
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await client.post("/api/auth/login", data=login_data)
        tokens = login_response.json()
        
        # Test token refresh
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        refresh_response = await client.post("/api/auth/refresh", json=refresh_data)
        
        assert refresh_response.status_code == 200
        refresh_tokens = refresh_response.json()
        assert "access_token" in refresh_tokens
        assert "refresh_token" in refresh_tokens
    
    async def test_logout(
        self, client: AsyncClient, test_user: User, auth_headers_user: dict
    ):
        """Test logout."""
        response = await client.post("/api/auth/logout", headers=auth_headers_user)
        
        assert response.status_code == 200
        assert "logged out" in response.json()["message"]