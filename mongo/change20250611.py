from pymongo import MongoClient
import pymongo

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ck = mongo_db["codekategorie"]
sem = mongo_db["semester"]
code = mongo_db["code"]

gebiete = [
    {"name" : "algebra", "beschreibung_de": "Algebra, Algebraische Geometrie, Arithmetische Geometrie, Zahlentheorie", "beschreibung_en" : "Algebra, algebraic geometry, arithmethmetic geometry, number theory"}, 
    {"name" : "analysis", "beschreibung_de": "Analysis", "beschreibung_en" : "Analysis"}, 
    {"name" : "numerik", "beschreibung_de": "Angewandte Analysis und Numerik", "beschreibung_en" : "Applied analysis and numerical mathematics"}, 
    {"name" : "didaktik", "beschreibung_de": "Fachdidaktik Mathematik", "beschreibung_en" : "Fachdidaktik Mathematik"}, 
    {"name" : "geometrie", "beschreibung_de": "Geometrie und Topologie", "beschreibung_en" : "Geometry and Topology"}, 
    {"name" : "logik", "beschreibung_de": "Mathematische Logik (Modelltheorie und Mengenlehre)", "beschreibung_en" : "Mathematical Logic (Model Theory and Set Theory)"}, 
    {"name" : "stochastik", "beschreibung_de": "Mathematische Stochastik und Finanzmathematik", "beschreibung_en" : "Probability theory and Financial Mathematics"}
]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

i = 0
j = 0
for s in sem.find():
    new_ck = ck.insert_one({"name_de" : "Schwerpunkte", "name_en" : "Focus areas", "komm_sichtbar" : False, "hp_sichtbar" : False, "beschreibung_de" : "", "beschreibung_en" : "", "semester": s["_id"], "kommentar" : "", "rang": i, "code" : []})
    i = i + 1
    for g in gebiete:
        c = {"codekategorie" : new_ck.inserted_id,
            "veranstaltung" : [],
            "kommentar" : "",
            "rang" : j,
            "semester" : s["_id"]
            }
        j = j + 1
        c = code.insert_one(g | c)
        sem.update_one({"_id" : s["_id"]}, { "$push" : { "code" : c.inserted_id}})
        ck.update_one({"_id" : new_ck.inserted_id}, { "$push" : { "code" : c.inserted_id}})
