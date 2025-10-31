# database.py
from motor.motor_asyncio import AsyncIOMotorClient



# client = AsyncIOMotorClient(MONGO_DETAILS)
# database = client["notes_app"]

# notes_collection = database.get_collection("notes")
# users_collection = database.get_collection("users")




# method for start the MongoDb Connection
async def startup_db_client(app):
    MONGO_DETAILS = "mongodb://localhost:27017"

    print("hello world")
    app.mongodb_client = AsyncIOMotorClient(MONGO_DETAILS)
    app.database = app.mongodb_client.get_database("notes_app")
    app.notes_collection = app.database["notes"]
    app.users_collection = app.database["users"]

    print("MongoDB connected.")

# method to close the database connection
async def shutdown_db_client(app):
    app.mongodb_client.close()
    print("Database disconnected.")

# def note_helper(note) -> dict:
#     return {
#         "id": str(note["_id"]),
#         "title": note.get("title"),
#         "content": note.get("content"),
#         "username": note.get("username"),
#     }

# def user_helper(user) -> dict:
#     return {
#         "id": str(user["_id"]),
#         "username": user.get("username"),
#         # DO NOT return password hash in API responses in production
#         "admin_status": user.get("admin_status", False),
#     }
