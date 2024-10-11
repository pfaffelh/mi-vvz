from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]


ver = mongo_db["veranstaltung"]
stu = mongo_db["studiengang"]
mod = mongo_db["modul"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20241002
#mongo_db.command('collMod','veranstaltung', validator=schema20241002.veranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# doppelte Module aus Studiengängen rausschmeißen und andersherum

allstu = list(stu.find())
allmod = list(mod.find())
for m in allmod:
    kurzname = m["kurzname"].replace("Mo-", "")
#    print(kurzname)
    mod.update_one({"_id" : m["_id"]}, { "$set" : { "kurzname": kurzname, "studiengang" : list(set(m["studiengang"]))}})

allstu = list(stu.find())
for s in allstu:
    stu.update_one({"_id" : s["_id"]}, { "$set" : { "modul" : list(set(s["modul"]))}})

# modul und studiengang abgleichen
for m in allmod:
    for s_id in m["studiengang"]:
        s = stu.find_one({"_id": s_id})
        if m["_id"] not in s["modul"]:
            print(f"Modul {m["kurzname"]} nicht in Studiengang {s["kurzname"]}")
            stu.update_one({"_id": s["_id"]}, { "$push" : { "modul" : m["_id"]}})
for s in allstu:
    for m_id in s["modul"]:
        m = mod.find_one({"_id": m_id})
        if m and s["_id"] not in m["studiengang"]:
            print(f"Studiengang {s["kurzname"]} nicht in Modul {m["kurzname"]}")
            mod.update_one({"_id": m["_id"]}, { "$push" : { "studiengang" : s["_id"]}})


# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','veranstaltung', validator=schema20241002.veranstaltung_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
