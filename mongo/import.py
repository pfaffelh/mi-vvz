from pymongo import MongoClient
import os

# This is the mongodb
os.system("mongo vvz --eval  'db.dropDatabase()'")
os.system("mongorestore --archive='vvz_backup'")

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

sem = mongo_db["semester"]
gebaeude = mongo_db["gebaeude"]
raum = mongo_db["raum"]
cod = mongo_db["code"]
kat = mongo_db["kategorie"]
mod = mongo_db["modul"]
per = mongo_db["person"]
stu = mongo_db["studiengang"]
anf = mongo_db["anforderung"]
anfkat = mongo_db["anforderungkategorie"]
ver = mongo_db["veranstaltung"]

# Ab hier wird die Datenbank verändert

# Veranstaltungen brauchen einen Rang und hp_sichtbar
veranstaltung = list(ver.find({}, sort = [("name_de",1)]))
i = 0
for v in veranstaltung:
    ver.update_one({"_id": v["_id"]}, {"$set": {"rang": i, "hp_sichtbar": True}})
    i = i+1
print("Update von Rang der Veranstaltungen")

# Module brauchen einen Rang
modul = list(mod.find({}, sort = [("name_de",1)]))
i = 0
for m in modul:
    mod.update_one({"_id": m["_id"]}, {"$set": {"rang": i}})
    i = i+1
print("Update von Rang der Modulen")

# person.semester darf keine Duplikate enthalten
person = list(per.find({}))
# person.sichtbar ist nur True wenn im aktuellen Semester
akt_sem = sem.find_one({"kurzname": "2024SS"})["_id"]
for p in person:
    per.update_one({"_id": p["_id"]}, {"$set": {"semester": list(set(p["semester"]))}})
    per.update_one({"_id": p["_id"]}, {"$set": {"sichtbar": True if akt_sem in list(set(p["semester"])) else False }})
  
# studiengang.modul darf keine Duplikate enthalten
studiengang = list(stu.find({}))
for s in studiengang:
    stu.update_one({"_id": s["_id"]}, {"$set": {"modul": list(set(s["modul"]))}})
    
# modul.studiengang darf keine Duplikate enthalten
modul = list(mod.find({}))
for m in modul:
    mod.update_one({"_id": m["_id"]}, {"$set": {"studiengang": list(set(m["studiengang"]))}})
    


# leere Person hinzufügen
z = per.find()
rang = (sorted(z, key=lambda x: x['rang'])[0])["rang"]-1
per.insert_one( {"name": "-",
             "vorname": "", 
             "name_prefix": "", 
             "titel": "", 
             "tel": "", 
             "email": "", 
             "sichtbar": True, 
             "hp_sichtbar": False,
             "semester": [x["_id"] for x in list(sem.find())],
             "veranstaltung": [],
             "rang": rang
    })

# leeren Studiengang hinzufügen
z = stu.find()
rang = (sorted(z, key=lambda x: x['rang'])[0])["rang"]-1
stu.insert_one( {
    "name": "-",
    "kurzname": "-",
    "rang": rang,
    "modul": [], 
    "kommentar": "", 
    "sichtbar": False
})

# leeres Modul hinzufügen
z = mod.find()
rang = (sorted(z, key=lambda x: x['rang'])[0])["rang"]-1
mod.insert_one( {
    "name_de": "-", 
    "name_en": "-", 
    "kurzname": "-", 
    "studiengang": [], 
    "sichtbar": False, 
    "rang": rang,
    "kommentar": ""
})

# leere Kategorie in jedem Semester hinzufügen
all_sem = list(sem.find())
for s in [x["_id"] for x in all_sem]:
    z = kat.find({"semester": s})
    rang = (sorted(z, key=lambda x: x['rang'])[0])["rang"]-1
    kat.insert_one( {   
        "hp_sichtbar": False, 
        "titel_de": "-", 
        "titel_en": "", 
        "untertitel_de": "", 
        "untertitel_en": "", 
        "rang": rang, 
        "semester": s, 
        "prefix_de": "", 
        "prefix_en": "", 
        "suffix_de": "", 
        "suffix_en": "", 
        "veranstaltung": [], 
        "kommentar":""
    })

# Ab hier wird das Schema gecheckt
import schema
mongo_db.command("collMod", "semester", validator = schema.semester_validator)
mongo_db.command("collMod", "gebaeude", validator = schema.gebaeude_validator)
mongo_db.command("collMod", "raum", validator = schema.raum_validator)
mongo_db.command("collMod", "person", validator = schema.person_validator)
mongo_db.command("collMod", "anforderung", validator = schema.anforderung_validator)
mongo_db.command("collMod", "anforderungkategorie", validator = schema.anforderungkategorie_validator)
mongo_db.command("collMod", "kategorie", validator = schema.kategorie_validator)
mongo_db.command("collMod", "code", validator = schema.code_validator)
mongo_db.command("collMod", "studiengang", validator = schema.studiengang_validator)
mongo_db.command("collMod", "modul", validator = schema.modul_validator)
mongo_db.command("collMod", "veranstaltung", validator = schema.veranstaltung_validator)






