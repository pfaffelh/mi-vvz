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
        semester_shortname = str.split(file, ".")[0].lower()
        sem = mongo_db["semester"]
        sem_id = sem.find_one({"id1": semester_shortname})['_id']
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
            if studiengang.find_one({'name': post['name']}):
                logging.debug("Already available: Skipped " + str(post['id']))
            else:
                studiengang.insert_one(post)

        for index, row in df.iterrows():
            stu = studiengang.find_one({'name': row['name']})
            if stu:
                studiengang.update_one({'name': row['name']}, {'$push': {'semester': sem_id}})
            else:
                print(f"Studiengang {row['id']} nicht gefunden")

    studiengang.update_many({}, {"$unset": {"id":1}}) 
