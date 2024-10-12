from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
sem = mongo_db["semester"]
mod = mongo_db["modul"]

# Semester bekommt neue Felder für den Vorspann der Modulhandbücher

import schema20241012
mongo_db.command('collMod','semester', validator=schema20241012.semester_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

sem.update_many({}, { "$set" : { "vorspann_kommentare_de" : "", "vorspann_kommentare_en" : ""}})

allver = list(ver.find())
allmod = list(mod.find())
for v in allver:
#    ver.update_one({"_id" : v["_id"]}, { "$set" : { "verwendbarkeit" : [ x for x in v["verwendbarkeit"] if x["modul"] in [y["_id"] for y in allmod] ]  }})

    for x in v["verwendbarkeit"]:
        try:
            mod.find_one({"_id" : x["modul"]})["_id"]
        except:
            print(f"Wrong module {x} in {v["name_de"]}")


# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','semester', validator=schema20241012.semester_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
