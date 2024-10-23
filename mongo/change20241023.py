from pymongo import MongoClient
import pymongo
import os
import datetime
import json
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

per = mongo_db["person"]
ver = mongo_db["veranstaltung"]

# Semester bekommt neue Felder für den Vorspann der Modulhandbücher

import schema20241023
mongo_db.command('collMod','person', validator=schema20241023.person_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

per.update_many({}, { "$set" : { "url" : ""}})

with open('ldap.json', 'r') as json_file:
    data = json.load(json_file)

for item in data:
    print(item)
    per.update_one({"vorname" : item["givenName"], "name" : item["sn"]}, {"$set" : { "url" : item["labeledURI"] if item["labeledURI"] is not None else "", "email" : item["mail"] if item["mail"] is not None else ""}})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','person', validator=schema20241023.semester_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
