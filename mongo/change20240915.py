from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

rub = mongo_db["rubrik"]
sem = mongo_db["semester"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

semester_list = list(sem.find())

for s in semester_list:
    try:
        k = rub.find_one({"semester": s["_id"], "titel_de": "-"})["_id"]
    except:
        print("Änderung")
        rub.insert_one({"titel_de": "-",
                "titel_en": "",
                "untertitel_de": "", 
                "untertitel_en": "", 
                "prefix_de": "", 
                "prefix_en": "", 
                "suffix_de": "", 
                "suffix_en": "", 
                "hp_sichtbar": False,
                "veranstaltung": [] ,
                "kommentar": "",
                "semester": s["_id"],
                "rang" : max([r["rang"] for r in rub.find({})]) + 1
        })
