import pymongo
from pymongo import MongoClient
import sqlite3
from sqlite3 import Error
import pandas as pd
from bson.objectid import ObjectId
import logging
logging.basicConfig(level=logging.DEBUG, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

import tools

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]
logging.info("Connected to MongoDB")
logging.info("Database contains collections: ")
logging.info(str(mongo_db.list_collection_names()))

pro = mongo_db["program"]
a = pro.find({'shortname': 'MSc'})
for b in a:
    logging.debug(b['name'])

file = "2023ss.db"
semester_id = str.split(file, ".")[0]
sem = mongo_db["semester"]
sem_id = ObjectId(sem.find_one({"name": semester_id}))
print(sem_id)
code = mongo_db["code"]
cod_id = (code.find({"name": "B"})[0])
print(ObjectId(cod_id['_id']))

