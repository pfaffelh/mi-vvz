import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId
import schema

def port(mongo_db, files):
    anf = mongo_db["anforderung"]
    anfkat = mongo_db["anforderungkategorie"]
    anfkat.drop()
    a = anfkat.insert_one({"name_de": "PL", "name_en": "", "rang": 3, "sichtbar": True, "kommentar": "Prüfungsleistung"})
    b = anfkat.insert_one({"name_de": "SL", "name_en": "", "rang": 2, "sichtbar": True, "kommentar": "Studienleistung"})
    c = anfkat.insert_one({"name_de": "Kommentar", "name_en": "", "rang": 1, "sichtbar": True, "kommentar": "Kommentar zu einer Anforderung"})
    anfkat_dict = {"exam": a.inserted_id, "study": b.inserted_id, "comment": c.inserted_id}
    anf.drop()
    i = 1
    for file in files:
        conn = sqlite3.connect(file)
        logging.info("Connected to " + file)
        # Get all data from sqlite3 and put into mongo_db
        df = pd.read_sql_query("SELECT * from Requirement", conn)
        df.sort_values(by = "name", inplace=True)
        # drop some columns which are not needed
        df["name_de"] = df["desc"]
        df["anforderungskategorie"] = [anfkat_dict[x] for x in df["type"]]               
        posts = df.to_dict('records')
        for x in posts:
            if not anf.find_one({'name_de': x['name_de']}):
               x["sichtbar"] = True
               x["name_en"] = ""
               x["kommentar"] = ""
               x["rang"] = i
               i = i+1
               anf.insert_one(x)

    logging.info("Inserted in collection anforderung")


