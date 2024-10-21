from pymongo import MongoClient
import pymongo
import os
import datetime


cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
sem = mongo_db["semester"]
mod = mongo_db["modul"]
rub = mongo_db["rubrik"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

ss25id = sem.find_one({"kurzname" : "2025SS"})["_id"]
ws24id = sem.find_one({"kurzname" : "2024WS"})["_id"]
allver = list(ver.find({"semester" : ss25id}))

for v in allver:
    if v["rang"] == 0:
        minrang = min([w["rang"] for w in list(ver.find({"semester" : ss25id}))])
        ver.update_one({"_id": v["_id"]}, {"$set" : {"rang" : minrang - 1}})

rubss25namen = [r["titel_de"] for r in list(rub.find({"semester" : ss25id}))]
rubws24 = list(rub.find({"semester" : ws24id}))

kopie = {ws24id: ss25id}

for k in list(rub.find({"semester": ws24id})):
    if k["titel_de"] not in rubss25namen:
        k_loc = k["_id"]
        del k["_id"] # andernfalls gibt es einen duplicate key error
        k["semester"] = ss25id
        k_new = rub.insert_one(k)
        kopie[k_loc] = k_new.inserted_id
        sem.update_one({"_id": ss25id}, {"$push": {"rubrik": k_new.inserted_id}})

