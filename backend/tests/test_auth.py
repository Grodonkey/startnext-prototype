"""Tests for authentication endpoints."""
import pytest


class TestRegistration:
    """Test user registration."""

    def test_register_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json=test_user_data)
        # Accept both 200 and 201 for created resource
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data

    def test_register_duplicate_email(self, client, registered_user, test_user_data):
        """Test registration with existing email fails."""
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        data = {
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        }
        response = client.post("/api/auth/register", json=data)
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Test registration with too short password."""
        data = {
            "email": "test@example.com",
            "password": "short",
            "full_name": "Test User"
        }
        response = client.post("/api/auth/register", json=data)
        assert response.status_code == 422


class TestLogin:
    """Test user login."""

    def test_login_success(self, client, registered_user):
        """Test successful login."""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        """Test login with wrong password."""
        login_data = {
            "email": registered_user["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401


class TestAuthenticatedUser:
    """Test authenticated user endpoints."""

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "id" in data

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_logout(self, client, auth_headers):
        """Test user logout."""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
