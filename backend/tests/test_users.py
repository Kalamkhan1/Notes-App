"""Tests for user endpoints."""
import pytest
from fastapi.testclient import TestClient
from models import User


def test_create_user_success(client: TestClient):
    """Test successful user creation."""
    response = client.post("/user/create-user", json={
        "username": "newuser",
        "password": "newpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert "password" not in data  # Password should not be in response
    assert data["admin_status"] is False


def test_create_user_duplicate(client: TestClient, test_user: User):
    """Test creating user with duplicate username."""
    response = client.post("/user/create-user", json={
        "username": "testuser",
        "password": "password"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_current_user(client: TestClient, auth_headers: dict):
    """Test getting current user details."""
    response = client.get("/user/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "password" not in data


def test_list_users_as_admin(client: TestClient, admin_headers: dict, test_user: User):
    """Test listing all users as admin."""
    response = client.get("/user/admin/list-all", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2  # At least admin and test user
    usernames = [u["username"] for u in users]
    assert "admin" in usernames
    assert "testuser" in usernames


def test_list_users_as_regular_user(client: TestClient, auth_headers: dict):
    """Test listing users as regular user (should fail)."""
    response = client.get("/user/admin/list-all", headers=auth_headers)
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]


def test_count_users_as_admin(client: TestClient, admin_headers: dict, test_user: User):
    """Test counting users as admin."""
    response = client.get("/user/admin/count-users", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert data["total_users"] >= 2


def test_delete_user_as_admin(client: TestClient, admin_headers: dict, test_user: User):
    """Test deleting a user as admin."""
    response = client.delete(f"/user/admin/delete/{test_user.id}", headers=admin_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_self_as_admin(client: TestClient, admin_headers: dict, admin_user: User):
    """Test admin cannot delete their own account."""
    response = client.delete(f"/user/admin/delete/{admin_user.id}", headers=admin_headers)
    assert response.status_code == 400
    assert "Cannot delete own account" in response.json()["detail"]


def test_delete_user_as_regular_user(client: TestClient, auth_headers: dict, admin_user: User):
    """Test regular user cannot delete users."""
    response = client.delete(f"/user/admin/delete/{admin_user.id}", headers=auth_headers)
    assert response.status_code == 403
