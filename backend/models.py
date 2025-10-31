# models.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Notes

class Title(BaseModel):
    id: Optional[str] = Field(alias="_id")
    title: Optional[str] = None
    
    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        return str(v)
    

class Note(Title):
    content: Optional[str] = None

class NoteWithUser(Note):
    username: str

class NoteCreate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    


# Users
class Username(BaseModel):
    username: str

class User(Username):
    admin_status: Optional[bool] = False


class UserInDB(User):
    password: str

class UserCreate(Username):
    password: str

# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


