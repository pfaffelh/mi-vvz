from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

sem = mongo_db["semester"]
anf = mongo_db["anforderung"]
anfkat = mongo_db["anforderungkategorie"]
ver = mongo_db["veranstaltung"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

s = sem.find_one({"kurzname" : "2024WS"})
v = ver.find_one({"semester" : s["_id"], "name_de" : "Algebra und Zahlentheorie"})
x = v["verwendbarkeit_anforderung"]
x.pop(1)
ver.update_one({"_id" : v["_id"]}, { "$set" : {"verwendbarkeit_anforderung" : x}})
print(1)
anf.insert_one({"name_de": "-",
                    "name_en": "",
                    "anforderungskategorie": anfkat.find_one({"name_de": "-"})["_id"],
                    "kommentar": "", 
                    "sichtbar": True,
                    "rang" : 300
        })

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
