from pymongo import MongoClient
import pymongo

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
sem = mongo_db["semester"]

for s in list(sem.find()):
    ve = list(ver.find({"semester" : s["_id"]}, sort = [("rang", pymongo.ASCENDING)]))
    for v in ve:
#        print(f"{v["kurzname"]}")
        w = ver.find_one({"_id" : {"$ne" : v["_id"]}, "rang" : v["rang"]})
        if w:
            print(f"Semester {s["kurzname"]}: {v["name_de"]} und {w["name_de"]} haben denselben Rang.")
        

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

i = 0
for s in list(sem.find()):
    ve = list(ver.find({"semester" : s["_id"]}, sort = [("rang", pymongo.ASCENDING)]))
    for v in ve:
        ver.update_one({"_id" : v["_id"]}, {"$set" : {"rang" : i}})
        i = i + 1

