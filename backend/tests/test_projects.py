"""Tests for project endpoints."""
import pytest


class TestProjects:
    """Test project endpoints."""

    def test_list_projects(self, client):
        """Test listing all projects."""
        response = client.get("/api/projects/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_project_not_found(self, client):
        """Test getting non-existent project."""
        response = client.get("/api/projects/nonexistent-slug")
        assert response.status_code == 404

    def test_create_project_unauthorized(self, client):
        """Test creating project without auth."""
        project_data = {
            "title": "Test Project",
            "short_description": "A test project",
            "description": "This is a test project description"
        }
        response = client.post("/api/projects/", json=project_data)
        assert response.status_code == 401

    def test_create_project(self, client, auth_headers):
        """Test creating a new project."""
        project_data = {
            "title": "Test Project",
            "slug": "test-project",
            "short_description": "A test project",
            "description": "This is a test project description",
            "funding_goal": 10000.0,
            "project_type": "crowdfunding"
        }
        response = client.post(
            "/api/projects/",
            json=project_data,
            headers=auth_headers
        )
        # Accept both 200 and 201 for created resource
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["title"] == project_data["title"]
        assert "slug" in data
        assert "id" in data

    def test_get_my_projects(self, client, auth_headers):
        """Test getting user's own projects."""
        response = client.get("/api/projects/my-projects", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_my_projects_unauthorized(self, client):
        """Test getting my projects without auth."""
        response = client.get("/api/projects/my-projects")
        assert response.status_code == 401


class TestProjectUpdate:
    """Test project update endpoints."""

    @pytest.fixture
    def created_project(self, client, auth_headers):
        """Create a project for testing."""
        project_data = {
            "title": "Update Test Project",
            "slug": "update-test-project",
            "short_description": "A project to update",
            "description": "This project will be updated",
            "funding_goal": 5000.0
        }
        response = client.post(
            "/api/projects/",
            json=project_data,
            headers=auth_headers
        )
        # Accept both 200 and 201 for created resource
        assert response.status_code in [200, 201]
        return response.json()

    def test_update_project(self, client, auth_headers, created_project):
        """Test updating a project."""
        update_data = {"title": "Updated Project Title"}
        response = client.put(
            f"/api/projects/{created_project['slug']}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Project Title"

    def test_update_project_unauthorized(self, client, created_project):
        """Test updating project without auth."""
        update_data = {"title": "Unauthorized Update"}
        response = client.put(
            f"/api/projects/{created_project['slug']}",
            json=update_data
        )
        assert response.status_code == 401

    def test_delete_project(self, client, auth_headers, created_project):
        """Test deleting a project."""
        response = client.delete(
            f"/api/projects/{created_project['slug']}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/api/projects/{created_project['slug']}")
        assert response.status_code == 404
