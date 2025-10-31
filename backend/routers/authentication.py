# routers/authenticaiton.py

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, APIRouter, HTTPException, status, Request

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from models import UserInDB, Token, TokenData

# Configuration Constants

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token validity duration


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

# Utility Functions for Password Management

def verify_password(plain_password, hashed_password):
    """
    Verify if the provided plain-text password matches the stored hash.
    """
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Generate a secure hash for the given password.
    """
    return password_hash.hash(password)


# User Retrieval and Authentication
async def get_user(request: Request, username: str):
    """
    Retrieve a user record from MongoDB by username.

    Returns:
        UserInDB object if user exists, else None.
    """
    user = await request.app.users_collection.find_one({"username": username})

    if user:
        return UserInDB(**user)
    return None



async def authenticate_user(request: Request, username: str, password: str):
    """
    Authenticate a user by verifying their username and password.

    Returns:
        User object if credentials are valid, otherwise False.
    """
    user = await get_user(request, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# JWT Token Management

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Generate a new JWT access token for the provided data payload.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Token Validation and Current User Retrieval

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], request: Request):
    """
    Decode and validate the JWT token to retrieve the current authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.

    Returns:
        UserInDB object for the authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(username=token_data.username, request=  request)
    if user is None:
        raise credentials_exception
    return user



# OAuth2 Login Endpoint

@router.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    OAuth2 login endpoint.

    Validates user credentials and issues a new JWT access token if valid.
    The token can then be used for accessing protected routes.

    Returns:
        Token object containing:
            - access_token: JWT string.
            - token_type: "bearer"
    """

    user = await authenticate_user(request, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": user.username}, access_token_expires
    )
    print("Login successful")
    return {"access_token": access_token, "token_type": "bearer"}