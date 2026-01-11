"""Tests for note endpoints."""
import pytest
import re
from fastapi.testclient import TestClient
from models import User, Note
from sqlmodel import Session

UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'


def test_create_note(client: TestClient, auth_headers: dict):
    """Test creating a note."""
    response = client.post("/notes/", json={
        "title": "Test Note",
        "content": "Test content"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "Test content"
    assert data["username"] == "testuser"
    # Verify UUID format
    assert re.match(UUID_PATTERN, data["id"])


def test_create_note_without_auth(client: TestClient):
    """Test creating note without authentication."""
    response = client.post("/notes/", json={
        "title": "Test",
        "content": "Test"
    })
    assert response.status_code == 401


def test_get_user_notes(client: TestClient, auth_headers: dict, session: Session, test_user: User):
    """Test getting user's notes."""
    # Create test notes
    note1 = Note(title="Note 1", content="Content 1", username=test_user.username)
    note2 = Note(title="Note 2", content="Content 2", username=test_user.username)
    session.add(note1)
    session.add(note2)
    session.commit()
    
    response = client.get("/notes/", headers=auth_headers)
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) >= 2
    titles = [n["title"] for n in notes]
    assert "Note 1" in titles
    assert "Note 2" in titles


def test_get_note_by_id(client: TestClient, auth_headers: dict, session: Session, test_user: User):
    """Test getting a specific note by UUID."""
    note = Note(title="Specific Note", content="Specific content", username=test_user.username)
    session.add(note)
    session.commit()
    session.refresh(note)
    
    response = client.get(f"/notes/{note.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note.id
    assert data["title"] == "Specific Note"


def test_get_note_not_found(client: TestClient, auth_headers: dict):
    """Test getting non-existent note."""
    fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
    response = client.get(f"/notes/{fake_uuid}", headers=auth_headers)
    assert response.status_code == 404


def test_get_other_user_note(client: TestClient, auth_headers: dict, session: Session):
    """Test user cannot access another user's note."""
    # Create note for different user
    other_note = Note(title="Other Note", content="Content", username="otheruser")
    session.add(other_note)
    session.commit()
    session.refresh(other_note)
    
    response = client.get(f"/notes/{other_note.id}", headers=auth_headers)
    assert response.status_code == 404  # Should not find it


def test_update_note(client: TestClient, auth_headers: dict, session: Session, test_user: User):
    """Test updating a note."""
    note = Note(title="Original", content="Original content", username=test_user.username)
    session.add(note)
    session.commit()
    session.refresh(note)
    
    response = client.put(f"/notes/{note.id}", json={
        "title": "Updated",
        "content": "Updated content"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["content"] == "Updated content"


def test_update_partial_note(client: TestClient, auth_headers: dict, session: Session, test_user: User):
    """Test partial update of a note."""
    note = Note(title="Original", content="Original content", username=test_user.username)
    session.add(note)
    session.commit()
    session.refresh(note)
    
    response = client.put(f"/notes/{note.id}", json={
        "title": "Updated Title Only"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title Only"
    assert data["content"] == "Original content"  # Should remain unchanged


def test_delete_note(client: TestClient, auth_headers: dict, session: Session, test_user: User):
    """Test deleting a note."""
    note = Note(title="To Delete", content="Content", username=test_user.username)
    session.add(note)
    session.commit()
    session.refresh(note)
    note_id = note.id
    
    response = client.delete(f"/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify deletion
    get_response = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_count_notes_as_admin(client: TestClient, admin_headers: dict, session: Session, test_user: User):
    """Test counting all notes as admin."""
    # Create some notes
    note1 = Note(title="Note 1", content="Content", username=test_user.username)
    note2 = Note(title="Note 2", content="Content", username="admin")
    session.add(note1)
    session.add(note2)
    session.commit()
    
    response = client.get("/notes/admin/count-notes", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_notes" in data
    assert data["total_notes"] >= 2


def test_count_notes_as_regular_user(client: TestClient, auth_headers: dict):
    """Test regular user cannot count all notes."""
    response = client.get("/notes/admin/count-notes", headers=auth_headers)
    assert response.status_code == 403
