from pymongo import MongoClient
import pymongo

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
ter = mongo_db["terminart"]
cod = mongo_db["code"]
pla_kat = mongo_db["planungkategorie"]
pla_ver = mongo_db["planungveranstaltung"]

import schema20241106
mongo_db.command('collMod','veranstaltung', validator=schema20241106.veranstaltung_validator, validationLevel='off')
mongo_db.command('collMod','terminart', validator=schema20241106.terminart_validator, validationLevel='off')

pla_kat.drop()

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# Bei Person und Anforderung die Liste der Semester sortieren
ver.update_many({}, { "$set" : { "komm_sichtbar" : False}})

c_list = list(cod.find({"name" : "Komm"}))
print([c for c in c_list])
for c in c_list:
    ver.update_many({ "code" : { "$elemMatch" : { "$eq" : c["_id"]}} }, { "$set" : { "komm_sichtbar" : True}})

# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','person', validator=schema20241106.person_validator, validationLevel='moderate')
mongo_db.command('collMod','planungveranstaltung', validator=schema20241106.planungveranstaltung_validator, validationLevel='moderate')
mongo_db.command('collMod','veranstaltung', validator=schema20241106.veranstaltung_validator, validationLevel='moderate')
mongo_db.command('collMod','terminart', validator=schema20241106.terminart_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
