from pymongo import MongoClient
import pymongo
import os
import datetime
import json
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

per = mongo_db["person"]
ver = mongo_db["veranstaltung"]
anf = mongo_db["anforderung"]

# Semester bekommt neue Felder für den Vorspann der Modulhandbücher

import schema20241104
mongo_db.command('collMod','person', validator=schema20241104.person_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

per.update_many({}, { "$set" : { "name_en" : ""}})

ver_list = list(ver.find())
for v in ver_list:
    for a in v["verwendbarkeit_anforderung"]:
        anf.update_one({"_id" : a}, { "$addToSet" : { "semester" : v["semester"]}})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','person', validator=schema20241104.person_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
