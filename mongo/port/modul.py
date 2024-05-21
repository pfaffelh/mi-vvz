import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId
import tools
import time

def port(mongo_db, files):
    mod = mongo_db["modul"]
    pro = mongo_db["studiengang"]
    mod.drop()
    i=0
    for file in files:
        conn = sqlite3.connect(file)
        logging.info("Connected to " + file)
         # Get all data from sqlite3 and put into mongo_db
        df = pd.read_sql_query("SELECT * from Module", conn)
        df["kurzname"] = df["id"]
        df["sichtbar"] = [True for x in df["kurzname"]]
        df["kommentar"] = ["" for x in df["kurzname"]]
        posts = df.to_dict('records')
        for x in posts:
            x["name_de"] = x["name"]
            x["name_en"] = ""
            x["studiengang"] = []
            logging.debug(x)
            x["rang"] = i
            i = i+1
            mod.insert_one(x)

            
    

        # Let us use the table ProgramModule
        df = pd.read_sql_query(f"SELECT * from ProgramModule INNER JOIN Program ON Program.id = ProgramModule.program_id", conn)
        for index, row in df.iterrows():
            studiengang = pro.find_one({'name': row['name']})['_id']
            modul = mod.find_one({'kurzname': row['module_id']})['_id']
            pro.update_one({'_id': studiengang}, {'$push': {'modul': modul}})
            mod.update_one({'_id': modul}, {'$push': {'studiengang': studiengang}})

        for p in list(pro.find()):
            pro.update_one({"_id": p["_id"]}, {"$set": {"modul": list(set(p['modul']))}})
        for m in list(mod.find()):
            mod.update_one({"_id": m["_id"]}, {"$set": {"studiengang": list(set(m['studiengang']))}})
