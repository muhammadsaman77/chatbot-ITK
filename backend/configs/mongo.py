from pymongo import MongoClient
import os

def init_mongodb():
    mongo_url = os.getenv("MONGO_URL")
    mongo_username = os.getenv("MONGO_USERNAME")
    mongo_password = os.getenv("MONGO_PASSWORD")
    mongo_database = os.getenv("MONGO_DATABASE")
    client = MongoClient(mongo_url,username=mongo_username, password=mongo_password)
    return client[mongo_database]
