from pymongo import MongoClient
from decouple import config

MONGO_URI = (f"mongodb+srv://{config('NOSQL_USER')}:{config('NOSQL_PASSWORD')}"
             f"@{config('NOSQL_HOST')}/{config('BD')}"
             f"?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=false")
MONGO_DB = config('BD')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

test_collection = db.test_collection
test_collection.insert_one({"test": "ok"})
result = test_collection.find_one({"test": "ok"})

if result:
    print("✅ Connection to MongoDB Atlas successful!")
else:
    print("❌ Failed to connect to MongoDB Atlas.")