from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import json_util
import json

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
db = client[os.getenv("DATABASE_NAME", "forgeapi")]

collections = db.list_collection_names()
print("Collections:", collections)

for name in collections:
    print("\n" + "=" * 60)
    print(f"Collection: {name}")
    print("=" * 60)

    count = db[name].count_documents({})
    print(f"Total documents: {count}")

    docs = list(db[name].find().limit(10))
    if docs:
        print(json.dumps(docs, indent=2, default=json_util.default))
    else:
        print("No documents found")