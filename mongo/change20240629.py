from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

sem = mongo_db["semester"]
ver = mongo_db["veranstaltung"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240629
mongo_db.command('collMod','semester', validator=schema20240629.semester_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# This gives a rang to 1. Vorlesung etc
allsems = list(sem.find({}))
i = 0
for s in allsems:
    sem.update_one({"_id": s["_id"]}, { "$set": {"prefix_de": "", "prefix_en": ""}})

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20240629
mongo_db.command("collMod", "semester", validator = schema20240629.semester_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
