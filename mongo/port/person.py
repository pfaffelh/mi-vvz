import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId
import tools
import time
import schema

def port(mongo_db, files):
    collection_name = 'person'
    per = mongo_db[collection_name]
    per.drop()
    for file in files:
        semester_shortname = str.split(file, ".")[0].lower()
        sem = mongo_db["semester"]
        sem_id = sem.find_one({"id1": semester_shortname})['_id']
        conn = sqlite3.connect(file)
        logging.info("Connected to " + file)
        # cur = conn.cursor()
        table_name = "Person"
        trans = {'cn': 'kurzname', 'firstname': 'vorname', 'firstname_abbr': 'name_prefix', 'degree': 'titel'}
        logging.debug("Entering " + table_name)
        df = pd.read_sql_query(f"SELECT * from {table_name}", conn)
        df['hp_sichtbar'] = [True for x in df['name']]
        df['sichtbar'] = [True for x in df['name']]
        df['rang'] = [int(x) for x in df['id']]
        df.drop(columns = ['id'], inplace = True)
        df['id'] = [x.lower() for x in df['name']]
        df.rename(columns = trans, inplace = True)
        posts = df.to_dict('records')
        for x in posts:
            x["tel"] = ""
            x["email"] = ""
            x["veranstaltung"] = []
            x["semester"] = []
            if per.find_one({'name': x['name']}):
                logging.debug("Already available: Skipped " + str(x['id']))
            else:
                per.insert_one(x)

        for index, row in df.iterrows():
            person = per.find_one({'name': row['name']})
            if person:
                per.update_one({'name': row['name']}, {'$push': {'semester': sem_id}})
            else:
                print(f"Person {row['id']} nicht gefunden")
#        logging.debug(posts)


