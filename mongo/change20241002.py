from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20241002
mongo_db.command('collMod','veranstaltung', validator=schema20241002.veranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# This introduces deputat 

# Anforderungskategorie bekommt "kurzname", initial mit name_de belegt
# name_de wird Kommentar
# Kommentar wird ""

allver = list(ver.find({}))
for a in allver:
    e = a["ects"]
    try:
        e = float(e)
    except:
        e = 6.0
    v = a["verwendbarkeit"]
    for x in v:
        x["ects"] = e
    ver.update_one({"_id": a["_id"]}, { "$set": {"ects": e, "verwendbarkeit": v, "kommentar_verwendbarkeit_de": "", "kommentar_verwendbarkeit_en": ""}})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','veranstaltung', validator=schema20241002.veranstaltung_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
