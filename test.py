from pymongo import MongoClient, ASCENDING
import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId
import time

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

gebaeude = mongo_db["gebaeude"]
    
geb = list(gebaeude.find({"sichtbar": True}, sort=[("rang", ASCENDING)]))
gebaeude_sichtbar = { x["_id"]: x["name_de"] for x in geb }

print(gebaeude_sichtbar)

