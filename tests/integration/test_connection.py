from pymongo import MongoClient
import os
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

test_collection = db.test_collection
test_collection.insert_one({"test": "ok"})
result = test_collection.find_one({"test": "ok"})

if result:
    print("✅ Connection to MongoDB Atlas successful!")
else:
    print("❌ Failed to connect to MongoDB Atlas.")