from pymongo import MongoClient
import pandas as pd

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]
per = mongo_db["person"]
geb = mongo_db["gebaeude"]
ck = mongo_db["personencodekategorie"]
code = mongo_db["personencode"]

import schema20260303

mongo_db.command('collMod','person', validator=schema20260303.person_validator, validationLevel='off')

# abschluss, kommentar zur abwesenheit, kommentag_dekanat hinzufügen
# ck dekanat hinzufügen

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

per.update_many({}, { "$set" : { "abschluss" : "", "kommentar_abwesend" : "", "kommentar_stelle" : ""}})

df = pd.read_excel("../../personen.xlsx", engine="openpyxl")
df = df.where(pd.notna(df), None)
liste = df.to_dict(orient="records")
print(df.head())

for p in liste:
    pe = per.find_one({"name" : p["name"], "vorname" : p["vorname"]})
    if pe:
        if p["abschluss"]:
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"abschluss" : p["abschluss"]}})
        if p["titel"]:
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"titel" : p["titel"]}})
        if p["gender"]:
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"gender" : p["gender"]}})
        if p["vorgesetzte"]:
            print(f"Vorgesetzer {p["vorgesetzte"]}")
            co = code.find_one({"name" : "Professorinnen und Professoren"})
            vo = per.find_one({"name" : p["vorgesetzte"]})
            per.update_one({"_id" : pe["_id"]}, {"$addToSet" : {"vorgesetzte" : vo["_id"]}})
        if p["abteilung"]:
            print(f"Abteilung {p["abteilung"]}")
            co = code.find_one({"name" : p["abteilung"]})
            per.update_one({"_id" : pe["_id"]}, {"$addToSet" : {"code" : co["_id"]}})
        if pd.notna(p["einstiegsdatum"]):
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"einstiegsdatum" : p["einstiegsdatum"]}})
        if pd.notna(p["ausstiegsdatum"]):
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"ausstiegsdatum" : p["ausstiegsdatum"]}})
        if pd.notna(p["abwesend_start"]):
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"abwesend_start" : p["abwesend_start"]}})
        if pd.notna(p["abwesend_ende"]):
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"abwesend_ende" : p["abwesend_ende"]}})
        if p["abwesend_kommentar"]:
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"abwesend_kommentar" : p["abwesend_kommentar"]}})
        if p["kommentar"]:
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"kommentar" : p["kommentar"]}})
        if p["dekanat"]:
            co = code.find_one({"name" : p["dekanat"]})
            #print(f"Fehler bei {p["dekanat"]}")
            per.update_one({"_id" : pe["_id"]}, {"$addToSet" : {"code" : co["_id"]}})
        if p["studiendekanat"]:
            co = code.find_one({"name" : p["studiendekanat"]})
            per.update_one({"_id" : pe["_id"]}, {"$addToSet" : {"code" : co["_id"]}})
    else:
        print(f"Warning: Person {p} nicht gefunden!")

df = pd.read_excel("../../personen2.xlsx", engine="openpyxl")
df = df.where(pd.notna(df), None)
liste = df.to_dict(orient="records")
print(df.head())

for p in liste:
    pe = per.find_one({"name" : p["name"]})
    if pe:
        if p["kennung"]:
            per.update_one({"_id" : pe["_id"]}, {"$set" : {"kennung" : p["kennung"]}})

#abschluss, titel, name, vorname, gender, abteilung, vorgesetzte, einstiegsdatum, dekanat, 


print("Check schema")
            

mongo_db.command('collMod','person', validator=schema20260303.person_validator, validationLevel='moderate')

