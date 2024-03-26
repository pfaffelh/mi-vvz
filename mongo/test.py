from pymongo import MongoClient, DESCENDING
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]
kat = mongo_db["kategorie"]
sem = mongo_db["semester"]

semesters = list(sem.find(sort=[("kurzname", DESCENDING)]))
semester = semesters[0]["_id"]

newkat = {"titel_de": "Neue Kategorie",
            "titel_en": "",
            "untertitel_de": "", 
            "untertitel_en": "", 
            "prefix_de": "", 
            "prefix_en": "", 
            "suffix_de": "", 
            "suffix_en": "", 
            "hp_sichtbar": True,
            "veranstaltung": [] ,
            "kommentar": "", 
            "rang": -100,
            "semester": semester
    }

x = kat.insert_one(newkat)
print(x.inserted_id)

