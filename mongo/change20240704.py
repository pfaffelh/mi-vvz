from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

codekategorie = mongo_db["codekategorie"]
ver = mongo_db["veranstaltung"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240704
mongo_db.command('collMod','codekategorie', validator=schema20240704.codekategorie_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# This introduces komm_sichtbar to all codekategorien

allck = list(codekategorie.find({}))
i = 0
for a in allck:
    codekategorie.update_one({"_id": a["_id"]}, { "$set": {"komm_sichtbar": False}})

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20240704
mongo_db.command("collMod", "codekategorie", validator = schema20240704.codekategorie_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
