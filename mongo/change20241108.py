from pymongo import MongoClient
import pymongo

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
ter = mongo_db["terminart"]
cod = mongo_db["code"]
pla_kat = mongo_db["planungkategorie"]
pla_ver = mongo_db["planungveranstaltung"]

import schema20241108
mongo_db.command('collMod','veranstaltung', validator=schema20241108.veranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# Bei Person und Anforderung die Liste der Semester sortieren
ve = ver.find()
for v in ve:
    de = v["deputat"]
    for d in de:
        d["kommentar_intern"] = ""
    ver.update_one({"_id" : v["_id"]}, { "$set" : { "deputat" : de }})
        
# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','veranstaltung', validator=schema20241108.veranstaltung_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
