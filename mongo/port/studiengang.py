import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId
import tools
import time

def port(mongo_db, files):
    studiengang = mongo_db["studiengang"]
    studiengang.drop()
    i = 0
    for file in files:
        conn = sqlite3.connect(file)
        logging.info("Connected to " + file)
        # Get all data from sqlite3 and put into mongo_db
        df = pd.read_sql_query("SELECT * from Program", conn)
        df["kurzname"] = df["id"]
        df["sichtbar"] = [True for x in df["kurzname"]]
        posts = df.to_dict('records')
        for post in posts:
            logging.debug(post)
            post["modul"] = []
            post["rang"] = i
            i = i+1
            post["modul"] = []
            post["kommentar"] = ""
            studiengang.insert_one(post)
    studiengang.update_many({}, {"$unset": {"id":1}}) 
