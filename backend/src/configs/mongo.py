from pymongo import AsyncMongoClient
from beanie import init_beanie
from ..models.user import User,Role
from ..models.document import MDocument
import os

async def init_mongodb():
    mongo_url = os.getenv("MONGO_URL")
    print(mongo_url)
    client = AsyncMongoClient(mongo_url)
    try:
        await client.admin.command("ping")
        print("✅ MongoDB connected")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)
        raise
    db = client.get_database("db-chatbot")
    print(db)
    if db is None:
        
        print(db)
    
        db = client[os.getenv("MONGO_DATABASE", "db-chatbot")]

    await init_beanie(database=db, document_models=[User,Role,MDocument])

