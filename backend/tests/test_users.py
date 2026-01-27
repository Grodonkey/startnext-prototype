"""Tests for user profile endpoints."""
import pytest


class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_profile(self, client, auth_headers):
        """Test getting user profile."""
        response = client.get("/api/users/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "full_name" in data
        assert "id" in data

    def test_get_profile_unauthorized(self, client):
        """Test getting profile without auth."""
        response = client.get("/api/users/profile")
        assert response.status_code == 401

    def test_update_profile(self, client, auth_headers):
        """Test updating user profile."""
        update_data = {"full_name": "Updated Name"}
        response = client.put(
            "/api/users/profile",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    def test_update_profile_unauthorized(self, client):
        """Test updating profile without auth."""
        update_data = {"full_name": "Updated Name"}
        response = client.put("/api/users/profile", json=update_data)
        assert response.status_code == 401


class TestPublicProfiles:
    """Test public profile endpoints."""

    def test_get_public_profile_not_found(self, client):
        """Test getting non-existent public profile."""
        response = client.get("/api/profiles/user/nonexistent-slug")
        assert response.status_code == 404

    def test_get_successful_starters(self, client):
        """Test getting successful starters list."""
        response = client.get("/api/profiles/starters/successful")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
