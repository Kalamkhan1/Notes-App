# routers/notes.py

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from typing import Annotated

from models import Note, NoteWithUser, User, Title, NoteCreate
from routers.authentication import get_current_user

router = APIRouter()


@router.post("/", response_description="Add new note", response_model=NoteWithUser)
async def create_note(note: NoteCreate, request: Request, user: Annotated[User, Depends(get_current_user)]):
    """
    Create a new note for the currently authenticated user.
    The note will be linked to the user's username.
    """
    note_data = jsonable_encoder(note)
    note_data["username"] = user.username
    new_note = await request.app.notes_collection.insert_one(note_data)
    created_note = await request.app.notes_collection.find_one({"_id": new_note.inserted_id})
    return created_note


@router.get("/", response_description="List all user notes", response_model=list[Title])
async def get_notes(request: Request, user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve all notes belonging to the authenticated user.
    Returns only titles for quick preview.
    """
    notes = []
    async for note in request.app.notes_collection.find({"username": user.username}):
        notes.append(note)
    print("Listed all User Notes")
    return notes

@router.get("/admin/all-notes", response_description="List all notes", response_model=list[Title])
async def get_notes_all(request: Request, admin: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve all notes belonging to all users.

    Accessible only to admin users (`admin_status=True`).

    Returns only titles for quick preview.
    """

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not admin.admin_status:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    notes = []
    async for note in request.app.notes_collection.find({}):
        notes.append(note)
    print("Listed all notes")
    return notes


@router.get("/{note_id}", response_description="Get a single note", response_model=Note)
async def get_note(note_id: str, request: Request, user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve a specific note by its ID.
    Only accessible if the note belongs to the authenticated user.
    """
    note = await request.app.notes_collection.find_one(
        {"_id": ObjectId(note_id), "username": user.username}
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    print("Got Note")
    return note



@router.put("/{note_id}", response_description="Update a note", response_model=Note)
async def update_note(
    note_id: str, note: NoteCreate, request: Request, user: Annotated[User, Depends(get_current_user)]
):
    """
    Update an existing note owned by the authenticated user.
    Returns the updated note document.
    """
    note_data = {k: v for k, v in note.model_dump().items() if v is not None}
    update_result = await request.app.notes_collection.update_one(
        {"_id": ObjectId(note_id), "username": user.username},
        {"$set": note_data},
    )
    if update_result.modified_count != 1:
        raise HTTPException(status_code=404, detail="Note not found or not owned by user")

    updated_note = await request.app.notes_collection.find_one({"_id": ObjectId(note_id)})
    print("Note updated")
    return updated_note

@router.delete("/{note_id}", response_description="Delete a note")
async def delete_note(note_id: str,request: Request, user: Annotated[User, Depends(get_current_user)]):
    """
    Delete a note owned by the authenticated user.
    Returns a confirmation message on success.
    """
    delete_result = await request.app.notes_collection.delete_one(
        {"_id": ObjectId(note_id), "username": user.username}
    )
    if delete_result.deleted_count == 1:
        raise HTTPException(status_code=404, detail="Note not found or not owned by user")
    print("Note deleted")
    return {"message": "Note deleted successfully"}

