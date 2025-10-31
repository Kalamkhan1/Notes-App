# routers/users.py

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.encoders import jsonable_encoder
from typing import Annotated

from routers.authentication import get_current_user
from models import User, UserCreate
from routers.authentication import get_password_hash

router = APIRouter(tags=["users"])


@router.post("/create-user", response_description="Create a new user", response_model=User)
async def create_user(request: Request, user: UserCreate):
    """
    Create a new user account.

    - Checks if the username already exists.
    - Hashes the password before storing it.
    - Returns the created user’s details (excluding password).
    """
    existing = await request.app.users_collection.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    json_user = jsonable_encoder(user)
    json_user["password"] = hashed_password

    result = await request.app.users_collection.insert_one(json_user)
    created = await request.app.users_collection.find_one({"_id": result.inserted_id})
    print("User created")
    return created


@router.get("/", response_description="Get user details", response_model=User)
async def get_user(request: Request, user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve the details of the currently authenticated user.

    - Requires valid authentication credentials.
    - Returns the user’s profile information.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result = await request.app.users_collection.find_one({"username": user.username})
    print("Got user details")
    return result


@router.get("/admin/list-all", response_description="List users (admin only)", response_model=list[User])
async def list_users(request: Request, admin: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve a list of all registered users.

    - Accessible only to admin users (`admin_status=True`).
    - Returns a list of all user records.
    """
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not admin.admin_status:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    users = []
    async for u in request.app.users_collection.find({}):
        users.append(u)
    print("Listed all users")
    return users
