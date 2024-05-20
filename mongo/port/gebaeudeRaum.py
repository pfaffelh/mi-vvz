import pandas as pd
import sqlite3
import logging
from bson.objectid import ObjectId
import tools
import time

def port(mongo_db, files):
    gebaeude = mongo_db["gebaeude"]
    gebaeude.drop()
#    gebaeude.create_index("id1", unique=True)

    raum = mongo_db["raum"]
    raum.drop()
#    ort.create_index("id1", unique=True)

    i=0
    n = 100
    k = 100
    for file in files:
        conn = sqlite3.connect(file)
        logging.info("Connected to " + file)
        # Get all data from sqlite3 and put into mongo_db
        df = pd.read_sql_query("SELECT * from Place", conn)
        df.rename(columns = {'building' : 'gebaeude'}, inplace=True)
        df['gebaeude'] = ["Ernst-Zermelo-Straße 1" if x == "Ernst-Zermelo-Str. 1" else x for x in df['gebaeude']]
        df['gebaeude'] = ["Hermann-Herder-Str. 10" if x == "Herman-Herder-Str. 10" else x for x in df['gebaeude']]
        df['gebaeude'] = ["Albertstraße 19" if x == "Albertsstr. 19" else x for x in df['gebaeude']]
        df['gebaeude'] = ["Physik Hochhaus" if x == "Physik-Hochhaus" else x for x in df['gebaeude']]
        posts = [{'name': x} for x in df['gebaeude']]
        df['gebaeude'] = ["Alte Uni" if x == "Alte Universität" else x for x in df['gebaeude']]
        posts = [{'name_de': x} for x in df['gebaeude']]
        for x in posts:
            x["name_en"] = ""
            x["adresse"] = ""
            x["url"] = ""
            x["sichtbar"] = (True if n < 130 else False)
            x["kommentar"] = ""
            x["kurzname"] = ""
            x['id1'] = "".join(([char for char in x['name_de'] if (char.isupper() or char.isnumeric())])).lower()
            x['url'] = ""
            x["rang"] = n
            n = n+1
            if (x["name_de"] == "") | (x['name_de'] is None) | (x['name_de'] == "-"):
                x["id1"] = "nn"
            if x["name_de"] == "online":
                x["id1"] = "online"
            if x['name_de'] == "Albertstr. 21a":
                x['id1'] = 'a21a'
            if x['name_de'] == "Raum noch nicht bekannt":
                x['id1'] = 'raumunbekannt'
            if x['name_de'] == "nach Ankündigung":
                x['id1'] = 'ankuendigung'            
            if x['name_de'] == "Pharmazie":
                x['id1'] = 'pharma'            
            if x['name_de'] == "Pädagogische Hochschule":
                x['id1'] = 'padh'

            #if (x['id1'] == "") | (x['id1'] is None):
            #    x['id1'] = "nn" + str(i)
            #    i = i+1
            if gebaeude.find_one({'id1': x['id1']}):
                logging.debug("Already available: Skipped " + x['name_de'])
            else:
                print(n)
                gebaeude.insert_one(x)
#        print(df['gebaeude'])
        for x in df['gebaeude']:
            if gebaeude.find_one({'name_de': x}) is None:
                logging.ERROR("Fehler kommt hier:")
                logging.ERROR(x)
        #print(df)
        #print(gebaeude.find_one({'name_de': "Raum noch nicht bekannt"}))
        raum.update_one({"kurzname": "online"}, {"$set": {"name_de": ""}})
        raum.update_one({"kurzname": "live"}, {"$set": {"name_de": ""}})
        
        df['gebaeude'] = [gebaeude.find_one({'name_de': x})['_id'] for x in df['gebaeude']]
        df.rename(columns = {'room': 'name_de', 'id': 'kurzname'}, inplace = True)
        df['id1'] = [x.lower() for x in df['kurzname']]
        # res = [char for char in test_str if char.isupper()]
        posts = df.to_dict('records')
        for x in posts:
            x["name_en"]=""
            x["raum"] = ""
            x["groesse"] = 0
            x["kommentar"] = ""
            x["sichtbar"] = (True if k < 130 else False)
            if raum.find_one({'id1': x['id1']}):
                logging.debug("Already available: Skipped " + x['id1'])
            else:
                x["rang"] = k
                k = k+1
                raum.insert_one(x)
        logging.debug(posts)
    gebaeude.update_one({"id1": "ezs1"}, { "$set": { "rang": 1, "kurzname": "EZ1" } })
    gebaeude.update_one({"id1": "hhs10"}, { "$set": { "rang": 2, "kurzname": "HH10" } })
    gebaeude.update_one({"id1": "a21"}, { "$set": { "rang": 3 } })
    gebaeude.update_one({"id1": "a21a"}, { "$set": { "rang": 4 } })

    gebaeude.update_many({}, {"$unset": {"id1":""}})
#    raum.update_many({}, {"$unset": {"id1":""}})
    gebaeude_leer = gebaeude.find_one({"name_de": "-"})
    raum.insert_one({"name_de": "-", "name_en": "", "kurzname": "", "gebaeude": gebaeude_leer["_id"], "raum": "", "groesse": 0, "sichtbar": True, "kommentar": "", "rang": 200})

    import schema
    mongo_db.command("collMod", "gebaeude", validator = schema.gebaeude_validator)
    mongo_db.command("collMod", "raum", validator = schema.raum_validator)

