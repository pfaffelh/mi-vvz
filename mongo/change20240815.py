from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240815
mongo_db.command('collMod','veranstaltung', validator=schema20240815.veranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# This introduces komm_sichtbar to all codekategorien

allver = list(ver.find({}))
for a in allver:
    wt = a["woechentlicher_termin"]
    for t in wt:
        t["kommentar_de_latex"] = t["kommentar_de"]
        t["kommentar_en_latex"] = t["kommentar_en"]
        t["kommentar_de_html"] = t["kommentar_de"]
        t["kommentar_en_html"] = t["kommentar_en"]
        del t["kommentar_de"]
        del t["kommentar_en"]
    et = a["einmaliger_termin"]
    for t in et:
        t["kommentar_de_latex"] = t["kommentar_de"]
        t["kommentar_en_latex"] = t["kommentar_en"]
        t["kommentar_de_html"] = t["kommentar_de"]
        t["kommentar_en_html"] = t["kommentar_en"]
        del t["kommentar_de"]
        del t["kommentar_en"]
    ver.update_one({"_id": a["_id"]}, { "$set": {"woechentlicher_termin": wt, "einmaliger_termin": et}})

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20240815
mongo_db.command("collMod", "veranstaltung", validator = schema20240815.veranstaltung_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
