"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from models import User


def test_login_success(client: TestClient, test_user: User):
    """Test successful login."""
    response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user: User):
    """Test login with wrong password."""
    response = client.post("/token", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user."""
    response = client.post("/token", data={
        "username": "nonexistent",
        "password": "password"
    })
    assert response.status_code == 401


def test_protected_route_without_token(client: TestClient):
    """Test accessing protected route without token."""
    response = client.get("/user/")
    assert response.status_code == 401


def test_protected_route_with_invalid_token(client: TestClient):
    """Test accessing protected route with invalid token."""
    response = client.get("/user/", headers={
        "Authorization": "Bearer invalid_token"
    })
    assert response.status_code == 401


def test_protected_route_with_valid_token(client: TestClient, auth_headers: dict):
    """Test accessing protected route with valid token."""
    response = client.get("/user/", headers=auth_headers)
    assert response.status_code == 200
