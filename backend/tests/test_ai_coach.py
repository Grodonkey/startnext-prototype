"""Tests for AI Coach endpoints."""
import pytest


class TestAICoachSettings:
    """Test AI Coach settings endpoint."""

    def test_get_settings(self, client):
        """Test getting AI Coach settings."""
        response = client.get("/api/ai-coach/settings")
        assert response.status_code == 200
        data = response.json()
        assert "max_anonymous_messages" in data
        assert "min_messages_for_project" in data
        assert "max_anonymous_drafts" in data


class TestAICoachGenerate:
    """Test AI Coach message generation."""

    def test_generate_without_session(self, client):
        """Test generation requires session_id."""
        response = client.post(
            "/api/ai-coach/generate",
            json={
                "message": "Test message"
            }
        )
        # Should return validation error without session_id
        assert response.status_code == 422


class TestAICoachThreads:
    """Test AI Coach thread endpoints."""

    def test_get_thread_not_found(self, client):
        """Test getting non-existent thread."""
        response = client.get("/api/ai-coach/threads/nonexistent-thread-id")
        assert response.status_code == 404

    def test_claim_thread_unauthorized(self, client):
        """Test claiming thread without auth."""
        response = client.post(
            "/api/ai-coach/threads/some-thread-id/claim"
        )
        assert response.status_code == 401


class TestAICoachDrafts:
    """Test AI Coach draft endpoints."""

    def test_get_draft_not_found(self, client):
        """Test getting non-existent draft."""
        response = client.get("/api/ai-coach/drafts/nonexistent-thread-id")
        assert response.status_code == 404

    def test_generate_draft_thread_not_found(self, client):
        """Test generating draft for non-existent thread."""
        response = client.post(
            "/api/ai-coach/drafts/generate/nonexistent-thread-id",
            json={}
        )
        # 404 if thread not found, 503 if OpenAI not configured (checked first)
        assert response.status_code in [404, 503]

    def test_update_draft_not_found(self, client):
        """Test updating non-existent draft."""
        response = client.patch(
            "/api/ai-coach/drafts/nonexistent-thread-id",
            json={"title": "New Title"}
        )
        assert response.status_code == 404

    def test_convert_draft_unauthorized(self, client):
        """Test converting draft without auth."""
        response = client.post(
            "/api/ai-coach/drafts/some-thread-id/convert"
        )
        assert response.status_code == 401
