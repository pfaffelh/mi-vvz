from pymongo import MongoClient
import sqlite3
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

# Take a table from the sqlitedb and put everything which is not yet available into the mongodb.
# In order to determine what is identical, use field_id.
# trans is a translation dictionary "name in sql" : "name in mongo"
def port_sqlite_to_mongo(conn, table_name, collection_name, field_id, trans= {}, skip = []):
    logging.debug("Entering " + table_name)
    df = pd.read_sql_query(f"SELECT * from {table_name}", conn)
    df.rename(columns = trans, inplace = True)
    df.drop(skip, axis='columns', inplace = True)
    collection = mongo_db[collection_name]
    posts = df.to_dict('records')
    logging.debug("posts before deleting stuff.")
    logging.debug(posts)
    for x in posts:
        for key, value in x.items():
            if pd.isna(x[key]):
                logging.debug("Deleted " + key)
                del x[key] 
    for x in posts:
        if collection.find_one({field_id: x[field_id]}):
            logging.debug("Already available: Skipped " + x[field_id])
            del x[field_id] 
    logging.debug("posts after deleting stuff.")
    logging.debug(posts)
    for post in posts:
        collection.insert_one(post)
        logging.debug("Added one post in " + collection_name)
    logging.info("Updated " + collection_name)

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]
file = "2023ss.db"
conn = sqlite3.connect(file)
df = pd.read_sql_query(f"SELECT * from Place", conn)
building_list = list(set(df['building']))
building = mongo_db["building"]
posts = [{"name": x} for x in building_list]
logging.debug(posts)
for post in posts:
    building.insert_one(post)
print("printing building:")
print(list(building.find({})))

port_sqlite_to_mongo(conn, table_name = 'Place', collection_name = 'location', field_id = '_id', trans = {'id': '_id'})

location = mongo_db["location"]
documents = location.find()
for document in documents:
    b = document.get("building")
    b_id = building.find_one({"name": document.get("building")})
    document["building"] = b_id["_id"]
    print(document)
