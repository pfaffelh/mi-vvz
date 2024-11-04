from pymongo import MongoClient
import pymongo
import os
import datetime
import json
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

sem = mongo_db["semester"]
per = mongo_db["person"]
ver = mongo_db["veranstaltung"]
anf = mongo_db["anforderung"]
dic = mongo_db["dictionary"]

import schema20241105
mongo_db.command('collMod','person', validator=schema20241105.person_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# Bei Person und Anforderung die Liste der Semester sortieren
for p in per.find():
    se = list(sem.find({"_id": {"$in": p["semester"]}}, sort=[("rang", pymongo.ASCENDING)]))
    per.update_one({"_id" : p["_id"]}, { "$set" : { "semester" :[s["_id"] for s in se] }})

for a in anf.find():
    se = list(sem.find({"_id": {"$in": a["semester"]}}, sort=[("rang", pymongo.ASCENDING)]))
    anf.update_one({"_id" : a["_id"]}, { "$set" : { "semester" :[s["_id"] for s in se] }})




# dictionary löschen
dic.drop()

# calendar auslesen und eintragen


# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','person', validator=schema20241105.person_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
