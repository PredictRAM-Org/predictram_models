from pymongo import MongoClient
import os

def get_mongo_client():
    mongo_url = os.getenv("MONGO_URI", "mongodb+srv://admin:admin@cluster0.wdfuc.mongodb.net/interns?retryWrites=true&w=majority")
    client = MongoClient(mongo_url)
    return client

def get_database(db_name="interns"):
    client = get_mongo_client()
    return client[db_name]
