from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Annotated
from sqlmodel import select

from models import Note, NoteCreate, NoteUpdate, NotePublic, User
from routers.authentication import get_current_user
from database import SessionDep
from limiter import limiter

router = APIRouter()

@router.post("/", response_description="Add new note", response_model=NotePublic)
@limiter.limit("20/minute")
def create_note(request: Request, note: NoteCreate, session: SessionDep, user: Annotated[User, Depends(get_current_user)]):
    """
    Create a new note for the currently authenticated user.
    """
    db_note = Note.model_validate(note, update={"username": user.username})
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note

@router.get("/", response_description="List all user notes", response_model=list[NotePublic])
@limiter.limit("60/minute")
def get_notes(request: Request, session: SessionDep, user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve all notes belonging to the authenticated user.
    """
    statement = select(Note).where(Note.username == user.username)
    notes = session.exec(statement).all()
    print("Listed all User Notes")
    return notes

# @router.get("/admin/all-notes", response_description="List all notes", response_model=list[NotePublic])
# def get_notes_all(session: SessionDep, admin: Annotated[User, Depends(get_current_user)]):
#     """
#     Retrieve all notes belonging to all users (admin only).
#     """
#     if not admin.admin_status:
#         raise HTTPException(status_code=403, detail="Admin privileges required")

#     notes = session.exec(select(Note)).all()
#     print("Listed all notes")
#     return notes

@router.get("/admin/count-notes", response_description="Count all notes", response_model=dict)
def count_notes(session: SessionDep, admin: Annotated[User, Depends(get_current_user)]):
    """
    Count total number of notes (admin only).
    """
    if not admin.admin_status:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    notes = session.exec(select(Note)).all()
    return {"total_notes": len(notes)}

@router.get("/{note_id}", response_description="Get a single note", response_model=NotePublic)
@limiter.limit("30/minute")
def get_note(request: Request, note_id: str, session: SessionDep, user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve a specific note by its ID.
    Only accessible if the note belongs to the authenticated user.
    """
    statement = select(Note).where(Note.id == note_id).where(Note.username == user.username)
    note = session.exec(statement).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    print("Got Note")
    return note

@router.put("/{note_id}", response_description="Update a note", response_model=NotePublic)
@limiter.limit("30/minute")
def update_note(
    request: Request,
    note_id: str,
    note: NoteUpdate,
    session: SessionDep,
    user: Annotated[User, Depends(get_current_user)]
):
    """
    Update an existing note owned by the authenticated user.
    """
    statement = select(Note).where(Note.id == note_id).where(Note.username == user.username)
    db_note = session.exec(statement).first()
    
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found or not owned by user")

    note_data = note.model_dump(exclude_unset=True)
    db_note.sqlmodel_update(note_data)
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    
    print("Note updated")
    return db_note

@router.delete("/{note_id}", response_description="Delete a note")
@limiter.limit("30/minute")
def delete_note(request: Request, note_id: str, session: SessionDep, user: Annotated[User, Depends(get_current_user)]):
    """
    Delete a note owned by the authenticated user.
    """
    statement = select(Note).where(Note.id == note_id).where(Note.username == user.username)
    note = session.exec(statement).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    session.delete(note)
    session.commit()
    
    print("Note deleted")
    return {"message": "Note deleted successfully"}
