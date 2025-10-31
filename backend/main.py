# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import notes, users, authentication
from database import startup_db_client, shutdown_db_client

# Description for Swagger UI and API documentation
description = """
Notes App API lets users securely manage their personal notes. 📝

## Authentication
- **Register** and **log in** users with JWT authentication.
- Each user can access only their own notes.

## Notes
- **Create**, **view**, **update**, and **delete** personal notes.
- Admin users can view all notes in the system.

## Users
- Retrieve your own profile information.
- Admins can list all registered users.
"""

# Define lifespan method for managing app startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to database...")
    await startup_db_client(app)
    yield
    print("Closing database connection...")
    await shutdown_db_client(app)

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "*", 
]


# FastAPI app instance with metadata
app = FastAPI(
    title="Notes App API",
    description=description,
    summary="A secure note-taking backend built with FastAPI and MongoDB.",
    version="1.0.0",
    contact={
        "name": "Notes App Support",
        "email": "support@notesapp.dev",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/user", tags=["users"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(authentication.router, tags=["authentication"])


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Notes App API is running."}
