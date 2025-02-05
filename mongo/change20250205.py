from pymongo import MongoClient
import pymongo

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
sem = mongo_db["semester"]

import schema20250205
mongo_db.command('collMod','semester', validator=schema20250205.semester_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# add wasserzeichen to semester

# TODO: standardtexte für wiederkehrende veranstaltungen

# label bei Veranstaltung ist kurzname im pdf

for s in sem.find():
    sem.update_one({"_id" : s["_id"]}, { "$set" : { "wasserzeichen_kommentare_de" : "", "wasserzeichen_kommentare_en" : "", }})

print("Check schema")
mongo_db.command('collMod','semester', validator=schema20250205.semester_validator, validationLevel='moderate')
