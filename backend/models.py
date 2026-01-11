import uuid
from typing import Optional
from sqlmodel import Field, SQLModel

# Token
class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: str | None = None

# Users
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    admin_status: bool = Field(default=False)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int

# Notes
class NoteBase(SQLModel):
    title: str | None = Field(default=None)
    content: str | None = Field(default=None)

class Note(NoteBase, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    username: str = Field(index=True)

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class NotePublic(NoteBase):
    id: str
    username: str
