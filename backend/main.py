from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from routers import notes, users, authentication
from database import create_db_and_tables
from limiter import limiter

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
    print("Creating tables...")
    create_db_and_tables()
    print("Tables created.")
    yield

origins = [
    "*", 
]

# FastAPI app instance with metadata
app = FastAPI(
    title="Notes App API",
    description=description,
    summary="A secure note-taking backend built with FastAPI and SQLModel.",
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

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router, prefix="/user")
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(authentication.router, tags=["authentication"])


# Root endpoint
@app.get("/")
def root():
    return {"message": "Notes App API is running."}
