from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
sem = mongo_db["semester"]
stu = mongo_db["studiengang"]
rub = mongo_db["rubrik"]
statistiksemester = mongo_db["statistiksemester"]
statistikveranstaltung = mongo_db["statistikveranstaltung"]

# Semester bekommt neue Felder für den Vorspann der Modulhandbücher

import schema20241019
mongo_db.command('collMod','statistiksemester', validator=schema20241019.statistiksemester_validator, validationLevel='off')
mongo_db.command('collMod','statistikveranstaltung', validator=schema20241019.statistikveranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")


statistiksemester.insert_one({"name" : "Einschreibezahlen", "rang" : 100, "semester" : [s["_id"] for s in sem.find({})], "studiengang" : [s["_id"] for s in stu.find({})], "stat" : [], "kommentar" : ""})

statistikveranstaltung.insert_one({"name" : "Anzahl Tutorate", "rang" : 100, "rubrik" : [r["_id"] for r in rub.find({})], "stat" : [], "kommentar" : ""})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','statistiksemester', validator=schema20241019.statistiksemester_validator, validationLevel='moderate')
mongo_db.command('collMod','statistikveranstaltung', validator=schema20241019.statistikveranstaltung_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
