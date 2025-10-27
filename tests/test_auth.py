"""
Unit tests for auth module
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.auth.service import AuthService
from app.modules.auth.schemas import UserCreate, UserLogin


def test_create_user(db: Session):
    """Test user creation"""
    service = AuthService(db)

    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role="doctor"
    )

    user = service.create_user(user_data)

    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.role == "doctor"


def test_authenticate_user(db: Session):
    """Test user authentication"""
    service = AuthService(db)

    # Create user first
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role="doctor"
    )
    service.create_user(user_data)

    # Test authentication
    login_data = UserLogin(username="testuser", password="password123")
    user = service.authenticate_user(login_data)

    assert user is not None
    assert user.username == "testuser"


def test_authenticate_user_wrong_password(db: Session):
    """Test authentication with wrong password"""
    service = AuthService(db)

    # Create user first
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role="doctor"
    )
    service.create_user(user_data)

    # Test authentication with wrong password
    login_data = UserLogin(username="testuser", password="wrongpassword")
    user = service.authenticate_user(login_data)

    assert user is None


def test_register_user_endpoint(client: TestClient):
    """Test user registration endpoint"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "doctor"
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"


def test_login_endpoint(client: TestClient):
    """Test login endpoint"""
    # First register user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "doctor"
    }
    client.post("/auth/register", json=user_data)

    # Then login
    login_data = {
        "username": "testuser",
        "password": "password123"
    }

    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "user" in data


def test_get_current_user_endpoint(client: TestClient):
    """Test get current user endpoint"""
    # Register and login
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "doctor"
    }
    register_response = client.post("/auth/register", json=user_data)
    token = register_response.json()["access_token"]

    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"