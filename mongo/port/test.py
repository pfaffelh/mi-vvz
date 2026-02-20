from pymongo import MongoClient
import json
 
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]
 
per = mongo_db["person"]

import schema20260301
schema = schema20260301.person_validator["$jsonSchema"]
 
invalid_docs = mongo_db.person.find({
    "$nor": [
        {"$jsonSchema": schema}
    ]
})
 
for doc in invalid_docs:
    print(doc["_id"])

per.update_one(
             {"_id": doc["_id"]},
             {"$set": {"_validation_check": True}},
             bypass_document_validation=False)
print(doc)



