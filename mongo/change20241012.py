from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
sem = mongo_db["semester"]

# Semester bekommt neue Felder für den Vorspann der Modulhandbücher
# 

import schema20241012
mongo_db.command('collMod','semester', validator=schema20241012.semester_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

sem.update_many({}, { "$set" : { "vorspann_kommentare_de" : "", "vorspann_kommentare_en" : ""}})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','semester', validator=schema20241012.semester_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
