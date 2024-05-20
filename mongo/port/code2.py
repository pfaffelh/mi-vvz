import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId

def port(mongo_db, files):
    code = mongo_db["code"]
    code.delete_many({})
    code.create_index("id", unique=True)
    for file in files:
        semester_shortname = str.split(file, ".")[0].lower()
        sem = mongo_db["semester"]
        sem_id = sem.find_one({"id": semester_shortname})['id']
        conn = sqlite3.connect(file)
        logging.info("Connected to " + file)
        # Get all data from sqlite3 and put into mongo_db
        df = pd.read_sql_query("SELECT * from Code", conn)
        df['rank'] = df['id'].astype('Int32')
        df['semester'] = [sem_id for x in df['id']]
        df['name'] = df['code']
        df['id'] = [sem_id + "-" + x.lower() for x in df['name']]
        # drop some columns which are not needed
        df.drop(['code'], axis='columns', inplace = True)
        posts = df.to_dict('records')
        logging.debug("Here are the posts:")
        for post in posts:
            logging.debug(post)
            code.insert_one(post)
            sem.update_one({'id': sem_id}, {'$push': {'codes': post['id']}})
        logging.info("Inserted in collection code")
        logging.debug("Updated semester " + semester_shortname)
    import schema
    mongo_db.command("collMod", "code", validator = schema.code_validator)
