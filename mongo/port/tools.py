import pymongo
from pymongo import MongoClient
import sqlite3
from sqlite3 import Error
import pandas as pd
from datetime import datetime
import logging

# logging.basicConfig(level=logging.INFO, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]
logging.info("Connected to MongoDB")

# Take a table from the sqlitedb and put everything which is not yet available into the mongodb.
# In order to determine what is identical, use field_id.
# trans is a translation dictionary "name in sql" : "name in mongo"
def df_to_mongo(df, collection_name, field_id):
    collection = mongo_db[collection_name]
    posts = df.to_dict('records')
    logging.debug("posts before deleting stuff:")
    logging.debug(posts)
    for x in posts:
        rem = []
        for key, value in x.items():
            if x[key] is None:
                rem.append(key)
        for a in rem:
            del x[a]
            logging.debug("Deleted " + key)

    for x in posts:
        value = x[field_id]
        if collection.find_one({field_id: value}):
            logging.debug("Already available: Skipped " + x[field_id])
        else:
            collection.insert_one(x)
    logging.info("Updated " + collection_name)    

def port_sqlite_to_mongo(conn, table_name, collection_name, field_id, trans= {}, skip = []):
    logging.debug("Entering " + table_name)
    df = pd.read_sql_query(f"SELECT * from {table_name}", conn)
    df.rename(columns = trans, inplace = True)
    df.drop(skip, axis='columns', inplace = True)
    df_to_mongo(df, collection_name, field_id)

def insert_many_if_new(collection_name, posts, field_name):
    collection = mongo_db[collection_name]
    for post in posts:
        if collection.find_one({field_name: post[field_name]}):
            posts.remove(post)
    collection.insert_many(posts)

def new_semester(end_dates):
    sorted(end_dates)
    start = end_dates[len(end_dates)-1]  
    if start.month == 4:
        name = str(start.year) + "ss"
        end = datetime(start.year, month = 10, day = 1)
    if start.month == 10:
        name = str(start.year) + "ws"
        end = datetime(start.year+1, month = 4, day = 1)
    return name, start, end

