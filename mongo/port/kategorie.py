import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId
import schema

def port(mongo_db, files):
#    mongo_db.command("collMod", "kategorie", validator = schema.kategorie_validator)
    kat = mongo_db["kategorie"]
    kat.delete_many({})
    for file in files:
        semester_shortname = str.split(file, ".")[0].lower()
        sem = mongo_db["semester"]
        sem_id = sem.find_one({"id1": semester_shortname})['_id']
        sem_id1 = sem.find_one({"id1": semester_shortname})['id1']

        conn = sqlite3.connect(file)
        logging.info("Connected to " + file)
        # Get all data from sqlite3 and put into mongo_db
        df = pd.read_sql_query("SELECT * from Category", conn)
        # drop some columns which are not needed
        df.sort_values("name", inplace=True)
        df['rang'] = df['id'].astype('Int32')
        #        df['rang'] = range(len(df))

        df['id'] = [sem_id1 + "-" + str.split(x.lower(), " ")[0] for x in df['name']]
        df['semester'] = [sem_id for x in df['id']]
#        df.loc[13, 'rang'] = 17
#        df.loc[15, 'rang'] = 18
        df['prefix_de'] = ""
#        df.loc[4, 'prefix_de'] = df.loc[0,'name']
#        df.loc[8, 'prefix_de'] = df.loc[1,'name']
#        df.loc[11, 'prefix_de'] = df.loc[2,'name']
#        df.loc[14, 'prefix_de'] = df.loc[3,'name']
#        df.drop(['category_id'], axis='columns', inplace = True)
#        df.drop(labels = [0,1,2,3], inplace = True)
        df['titel_de'] = df['name']
        df['untertitel_de'] = [x if x is not None else "" for x in df['notes']]
        df.drop(['name', 'rank', 'notes'], axis='columns', inplace = True)
        posts = df.to_dict('records')
        for x in posts:
            if pd.isna(x['rang']):
                logging.debug("Deleted " + x['rang'])
                del x['rang']
#           if cat.find_one({'name': x['name']}):
#               logging.debug("Already available: Skipped " + x['name'] + " from " + file)
#               del x['name'] 
        logging.debug("Here are the posts:")
        for post in posts:
            logging.debug(post)
            post["prefix_en"] = ""
            post["titel_en"] = ""
            post["untertitel_en"] = ""
            post["suffix_de"] = ""
            post["suffix_en"] = ""
            post["kommentar"] = ""
            post["hp_sichtbar"] = True
            post["veranstaltung"] = []
            a = kat.insert_one(post)
            sem.update_one({'_id': sem_id}, {'$push': {'kategorie': a.inserted_id}})
        logging.info("Inserted in collection course_category")


