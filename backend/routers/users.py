# routers/users.py

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Annotated
from sqlmodel import select

from routers.authentication import get_current_user, get_password_hash
from models import User, UserCreate, UserPublic, Note
from database import SessionDep
from limiter import limiter

router = APIRouter(tags=["users"])


@router.post("/create-user", response_description="Create a new user", response_model=UserPublic)
@limiter.limit("3/minute")
def create_user(request: Request, user: UserCreate, session: SessionDep):
    """
    Create a new user account.
    """
    statement = select(User).where(User.username == user.username)
    existing = session.exec(statement).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    db_user = User.model_validate(user, update={"password": hashed_password})
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    print("User created")
    return db_user


@router.get("/", response_description="Get user details", response_model=UserPublic)
def get_user(user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve the details of the currently authenticated user.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


@router.get("/admin/list-all", response_description="List users (admin only)", response_model=list[UserPublic])
def list_users(session: SessionDep, admin: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve a list of all registered users (admin only).
    """
    if not admin.admin_status:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    users = session.exec(select(User)).all()
    print("Listed all users")
    return users


@router.get("/admin/count-users", response_description="Count all users", response_model=dict)
def count_users(session: SessionDep, admin: Annotated[User, Depends(get_current_user)]):
    """
    Count total number of users (admin only).
    """
    if not admin.admin_status:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    users = session.exec(select(User)).all()
    return {"total_users": len(users)}


@router.delete("/admin/delete/{user_id}", response_description="Delete a user (admin only)")
def delete_user(user_id: int, session: SessionDep, admin: Annotated[User, Depends(get_current_user)]):
    """
    Delete a user by ID and all their notes (admin only).
    Cannot delete own account.
    """
    if not admin.admin_status:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete own account")    
    
    statement = select(User).where(User.id == user_id)
    user_to_delete = session.exec(statement).first()
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Delete all notes associated with this user
    notes_statement = select(Note).where(Note.username == user_to_delete.username)
    user_notes = session.exec(notes_statement).all()
    for note in user_notes:
        session.delete(note)
    
    session.delete(user_to_delete)
    session.commit()
    
    print(f"User {user_id} and their {len(user_notes)} notes deleted by admin {admin.username}")
    return {"message": f"User and {len(user_notes)} notes deleted successfully"}