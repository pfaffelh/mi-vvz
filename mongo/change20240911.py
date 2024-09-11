from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
per = mongo_db["person"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240911
mongo_db.command('collMod','veranstaltung', validator=schema20240911.veranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# This introduces deputat 

allver = list(ver.find({}))
for a in allver:
    personen = a["dozent"] + a["assistent"] + a["organisation"]
    for t in a["woechentlicher_termin"]:
        personen = personen + t["person"]
    for t in a["einmaliger_termin"]:
        personen = personen + t["person"]
    personen = list(set(personen))
    personen = list(per.find({"_id" : { "$in" : personen}}, sort=[("name", pymongo.ASCENDING)]))
    personen = [p["_id"] for p in personen]
    deputat = [{"person" : p, "sws": 0.0} for p in personen]
    ver.update_one({"_id": a["_id"]}, { "$set": {"deputat": deputat}})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command("collMod", "veranstaltung", validator = schema20240911.veranstaltung_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
