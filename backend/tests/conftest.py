"""Test configuration and fixtures."""
import os
import sys

# Set test environment variables BEFORE importing anything from the app
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32chars"
os.environ["RESEND_API_KEY"] = "re_test_key"
os.environ["FROM_EMAIL"] = "test@example.com"
os.environ["ADMIN_EMAIL"] = "admin@test.com"
os.environ["ADMIN_PASSWORD"] = "testpassword123"
os.environ["FRONTEND_URL"] = "http://localhost:5173"
os.environ["BACKEND_URL"] = "http://localhost:8000"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create test database engine with SQLite BEFORE importing app modules
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Now import app modules - they will use the test environment
from database import Base, get_db
import models

# Create all tables in the test database
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    """Override database dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up the test database once per session."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Clean up
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Clear all data from tables
    for table in reversed(Base.metadata.sorted_tables):
        TestingSessionLocal().execute(table.delete())

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with fresh database."""
    from fastapi.testclient import TestClient
    from main import app

    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db

    # Clear all data before each test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user registration data."""
    return {
        "email": "testuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Register a test user and return credentials."""
    response = client.post("/api/auth/register", json=test_user_data)
    # Accept both 200 and 201 for created resource
    assert response.status_code in [200, 201], f"Registration failed: {response.json()}"
    return test_user_data


@pytest.fixture
def auth_headers(client, registered_user):
    """Get authentication headers for a logged-in user."""
    login_data = {
        "email": registered_user["email"],
        "password": registered_user["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, db_session):
    """Get authentication headers for admin user."""
    from security import get_password_hash

    # Create admin user for test
    admin = models.User(
        email="admin@test.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Admin User",
        profile_slug="admin-user",
        is_active=True,
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()

    # Login as admin
    login_data = {
        "email": "admin@test.com",
        "password": "testpassword123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200, f"Admin login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
