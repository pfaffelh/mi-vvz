from pymongo import MongoClient
import pymongo

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

ver = mongo_db["veranstaltung"]
sem = mongo_db["semester"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

i = 0    
for k in range(2010, 2018):
    sem.insert_one({"kurzname" : f"{k}WS",
                    "name_de" : f"Wintersemester {k}",
                    "name_en" : f"Winter term {k}",
                    "rang" : i,
                    "rubrik" : [],
                    "code" : [],
                    "veranstaltung" : [],
                    "hp_sichtbar" : False,
                    "vorspann_kommentare_de" : "", 
                    "vorspann_kommentare_en" : ""
                    })
    i = i+1
    sem.insert_one({"kurzname" : f"{k+1}SS",
                    "name_de" : f"Sommersemester {k+1}",
                    "name_en" : f"Summer term {k+1}",
                    "rang" : i,
                    "rubrik" : [],
                    "code" : [],
                    "veranstaltung" : [],
                    "hp_sichtbar" : False,
                    "vorspann_kommentare_de" : "", 
                    "vorspann_kommentare_en" : ""
                    })
    i = i+1

print([s["kurzname"] for s in list(sem.find(sort = [("rang", pymongo.ASCENDING)]))])