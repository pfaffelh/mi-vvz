from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
per = mongo_db["person"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240912
mongo_db.command('collMod','veranstaltung', validator=schema20240912.veranstaltung_validator, validationLevel='off')
mongo_db.command('collMod','person', validator=schema20240912.person_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# This introduces deputat 

allver = list(ver.find({}))
for a in allver:
    deputat = a["deputat"]
    deputat = [{"person" : d["person"], "sws": d["sws"], "kommentar" : ""} for d in deputat]
    ver.update_one({"_id": a["_id"]}, { "$set": {"deputat": deputat}})

allper = list(ver.find({}))
for p in allper:
    per.update_one({"_id": p["_id"]}, { "$set": {"kommentar": ""}})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command("collMod", "veranstaltung", validator = schema20240912.veranstaltung_validator, validationLevel='moderate')
mongo_db.command("collMod", "person", validator = schema20240912.person_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
