from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
anfkat = mongo_db["anforderungkategorie"]
anf = mongo_db["anforderung"]
sem = mongo_db["semester"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20241001
mongo_db.command('collMod','anforderungkategorie', validator=schema20241001.anforderungkategorie_validator, validationLevel='off')
mongo_db.command('collMod','anforderung', validator=schema20241001.anforderung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# This introduces deputat 

# Anforderungskategorie bekommt "kurzname", initial mit name_de belegt
# name_de wird Kommentar
# Kommentar wird ""

allanfkat = list(anfkat.find({}))
for a in allanfkat:
    kommentar = a["kommentar"] if a["kommentar"] != "" else a["name_de"]
    name_de = a["name_de"]
    anfkat.update_one({"_id": a["_id"]}, { "$set": {"name_de": kommentar, "kurzname": name_de, "kommentar": ""}})

allanf = list(anf.find({}))
s = sem.find_one({"kurzname" : "2024SS"})
for a in allanf:
    anf.update_one({"_id": a["_id"]}, {"$set" : {"semester" : [s["_id"]]}})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','anforderungkategorie', validator=schema20241001.anforderungkategorie_validator, validationLevel='moderate')
mongo_db.command('collMod','anforderung', validator=schema20241001.anforderung_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
