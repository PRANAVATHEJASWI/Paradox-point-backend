from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URL)
db = client["user_db"]
users_collection = db["users"]
