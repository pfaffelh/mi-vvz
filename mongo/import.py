from pymongo import MongoClient
import pymongo
import os
import datetime

# This is the mongodb
# Create mongodump using
# mongodump --db vvz --archive=vvz_backup

os.system("mongo vvz --eval 'db.dropDatabase()'")
os.system("mongorestore --archive='vvz_backup_neu'")  # Should be executed from mi-vvz/mongo/

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
import schema
mongo_db.command('collMod','veranstaltung', validator=schema.veranstaltung_validator, validationLevel='off')
mongo_db.command('collMod','semester', validator=schema.semester_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")
kat.rename("rubrik")
rub = mongo_db["rubrik"]
for s in sem.find():
    sem.update_one({"_id": s["_id"]}, {"$set": {"rubrik": s["kategorie"]}})
 #   sem.update_one({"_id": s["_id"]}, {"$unset": {"kategorie": ""}})

for v in ver.find():
    ver.update_one({"_id": v["_id"]}, {"$set": {"rubrik": v["kategorie"]}})
#    ver.update_one({"_id": v["_id"]}, {"$unset": {"kategorie": ""}})

#sem.update_many({}, { "$rename": { "kategorie": "rubrik" }})
#ver.update_many({}, { "$rename": { "kategorie": "rubrik" }})

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

# 
for v in ver.find():
    for p in list(set(v["dozent"] + v["assistent"] + v["organisation"])):
        per.update_one({"_id": p}, {"$push": {"veranstaltung": v["_id"]}})
for p in per.find():
        per.update_one({"_id": p}, {"$set": {"veranstaltung": list(dict.fromkeys(p["veranstaltung"]).keys())}})

# Veranstaltungen brauchen einen Rang und hp_sichtbar
veranstaltung = list(ver.find({}, sort = [("name_de",1)]))
i = 0
for v in veranstaltung:
    ver.update_one({"_id": v["_id"]}, {"$set": {"rang": i, "hp_sichtbar": True}})
    i = i+1
print("Update von Rang der Veranstaltungen")

# veranstaltung.verwendbarkeit_modul darf keine Duplikate enthalten
veranstaltung = list(ver.find({}))
for v in veranstaltung:
    ver.update_one({"_id": v["_id"]}, {"$set": {"verwendbarkeit_modul": list(dict.fromkeys(v["verwendbarkeit_modul"]).keys())}})
    ver.update_one({"_id": v["_id"]}, {"$set": {"verwendbarkeit_anforderung": list(dict.fromkeys(v["verwendbarkeit_anforderung"]).keys())}})
# veranstaltung.woechentlicher_termin.raum muss besetzt sein
veranstaltung = list(ver.find({}))
# leerer wöchentlicher Termin:
leerer_termin = {
    "key": "",
    "kommentar": "",
    "wochentag": "",
    "raum": raum.find_one({"name_de": "-"})["_id"],
    "person": [],
    "start": None,
    "ende": None
}
leerer_termin2 = {
    "key": "",
    "kommentar": "",
    "raum": [],
    "person": [],
    "startdatum": datetime.datetime(year = 1970, month = 1, day = 1, hour = 0, minute = 0),
    "startzeit": None,
    "endedatum": datetime.datetime(year = 1970, month = 1, day = 1, hour = 0, minute = 0),
    "endzeit": None
}

for v in veranstaltung:
    wt = v["woechentlicher_termin"]
    ver.update_one({"_id": v["_id"]}, {"$set": {"woechentlicher_termin": []}})
    for w in wt:
        termin = {}
        for key, value in leerer_termin.items():
            termin[key] = value
        for key, value in w.items():
            termin[key] = value
        ver.update_one({"_id": v["_id"]}, {"$push": {"woechentlicher_termin": termin}})
    wt = v["einmaliger_termin"]
    ver.update_one({"_id": v["_id"]}, {"$set": {"einmaliger_termin": []}})
    for w in wt:
        termin = leerer_termin2
        for key, value in w.items():
            if key == "start":
                termin["startdatum"] = value
                termin["startzeit"] = value
            elif key == "ende":
                termin["enddatum"] = value
                termin["endzeit"] = value
            else:
                termin[key] = value
        ver.update_one({"_id": v["_id"]}, {"$push": {"einmaliger_termin": termin}})
#        ver.update_one({"_id": v["_id"], "woechentlicher_termin.start": { "$exists": False }}, {"$set": {"woechentlicher_termin.0.start": datetime.datetime(year = 1970, month = 1, day = 1, hour = 0, minute = 0)}})
#ver.update_one({"_id": v["_id"], "woechentlicher_termin.start": { "$exists": False }}, {"$set": {"woechentlicher_termin.0.start": datetime.datetime(year = 1970, month = 1, day = 1, hour = 0, minute = 0)}})
#    ver.update_one({"_id": v["_id"], "woechentlicher_termin.end": { "$exists": False }}, {"$set": {"woechentlicher_termin.0.end": datetime.datetime(year = 1970, month = 1, day = 1, hour = 0, minute = 0)}})
#    ver.update_one({"_id": v["_id"], "woechentlicher_termin.raum": { "$exists": False }}, {"$set": {"woechentlicher_termin.0.raum": raum.find_one({"name_de": "-"})["_id"]}})
#    ver.update_one({"_id": v["_id"], "woechentlicher_termin.wochentag": { "$exists": False }}, {"$set": {"woechentlicher_termin.0.wochentag": "Sonntag"}})

# kein wöchtenlicher Termin mit nur "Assistenz"
ver.update_many({}, {"$pull": {"woechentlicher_termin": {"key": {"$eq": "Assistenz"}}}})


# Module brauchen einen Rang
modul = list(mod.find({}, sort = [("name_de",1)]))
i = 0
for m in modul:
    mod.update_one({"_id": m["_id"]}, {"$set": {"rang": i}})
    i = i+1
print("Update von Rang der Modulen")
# Module, die es in keinem Studiengang gibt, löschen:
mod.delete_many({"studiengang": []})
# Studiengänge ohne Module löschen:
stu.delete_many({"modul": []})

# person.semester darf keine Duplikate enthalten
person = list(per.find({}))
# person.sichtbar ist nur True wenn im aktuellen Semester
akt_sem = sem.find({}, sort=[("rang", pymongo.DESCENDING)])[0]["_id"]
for p in person:
    print(p['name'])
    l = list(dict.fromkeys(p["semester"]).keys())
    l.reverse()
    per.update_one({"_id": p["_id"]}, {"$set": {"semester": (l)}})
    per.update_one({"_id": p["_id"]}, {"$set": {"sichtbar": True if akt_sem in list(set(p["semester"])) else False }})

# studiengang.modul darf keine Duplikate enthalten
studiengang = list(stu.find({}))
for s in studiengang:
    stu.update_one({"_id": s["_id"]}, {"$set": {"modul": list(dict.fromkeys(s["modul"]).keys())}})
    
# modul.studiengang darf keine Duplikate enthalten
modul = list(mod.find({}))
for m in modul:
    mod.update_one({"_id": m["_id"]}, {"$set": {"studiengang": list(dict.fromkeys(m["studiengang"]).keys())}})

# leeren Studiengang hinzufügen
z = stu.find()
rang = (sorted(z, key=lambda x: x['rang'], reverse=True)[0])["rang"]+1
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
rang = (sorted(z, key=lambda x: x['rang'], reverse=True)[0])["rang"]+1
mod.insert_one( {
    "name_de": "-", 
    "name_en": "-", 
    "kurzname": "-", 
    "studiengang": [], 
    "sichtbar": False, 
    "rang": rang,
    "kommentar": ""
})

# leere Anforderungkategorie hinzufügen
z = anfkat.find()
rang = (sorted(z, key=lambda x: x['rang'], reverse=True)[0])["rang"]+1
anfkat.insert_one( {
    "name_de": "-", 
    "name_en": "", 
    "sichtbar": False, 
    "rang": rang,
    "kommentar": ""
})

# leere Kategorie in jedem Semester hinzufügen
all_sem = list(sem.find())
for s in [x["_id"] for x in all_sem]:
    z = rub.find({"semester": s})
    rang = (sorted(z, key=lambda x: x['rang'], reverse = True)[0])["rang"]+1
    rub.insert_one( {   
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

gebaeude_mit_url = {
    "Geb. 101, Georges-Köhler-Allee": "https://www.openstreetmap.org/?mlat=48.01251&mlon=7.83492#map=19/48.01251/7.83492",
    "Albertstr. 23b": "https://www.openstreetmap.org/?mlat=48.00233\&mlon=7.84788\#map=19/48.00233/7.84788",
    "Albertstr. 21": "https://www.openstreetmap.org/?mlat=48.00156\&mlon=7.84931\#map=19/48.00156/7.84931",
    "Albertstr. 21a": "https://www.openstreetmap.org/?mlat=48.00170\&mlon=7.84946\#map=19/48.00170/7.84946",
    "Ernst-Zermelo-Straße 1": "https://www.openstreetmap.org/?mlat=48.00065\&mlon=7.84591\#map=19/48.00065/7.84591",
    "Hermann-Herder-Str. 10": "https://www.openstreetmap.org/?mlat=48.00351\&mlon=7.84815\#map=19/48.00351/7.84815",
    "Stefan-Meier-Str. 26": "https://www.openstreetmap.org/?mlat=48.00248\&mlon=7.84681\#map=19/48.00248/7.84681",
#    "Fakultätssitzungsraum, Ernst-Zermelo-Straße 1": "https://www.openstreetmap.org/?mlat=48.00065\&mlon=7.84591\#map=19/48.00065/7.84591",
    "PH Freiburg": "https://www.openstreetmap.org/?mlat=47.98132\&mlon=7.89420\#map=17/47.98132/7.89420",
    "Oltmannstraße 22": "https://www.openstreetmap.org/?mlat=47.98021\&mlon=7.82836\#map=19/47.98021/7.82836",
#    "Breisacher Tor": "https://www.openstreetmap.org/?mlat=47.99252\&mlon=7.84775\#map=19/47.99252/7.84775"
}

for key, value in gebaeude_mit_url.items():
    g = gebaeude.find_one_and_update({"name_de": key}, { "$set": {"url": value}}, upsert = True)
    raum.update_many({"gebaeude": gebaeude.find_one({"name_de": f'<a href="{value}">{key}</a>'})["_id"]}, { "$set": { "gebaeude": g["_id"]}})
    gebaeude.delete_many({"name_de": f'<a href="{value}">{key}</a>'})

g = gebaeude.find_one_and_update({"name_de": "Fakultätssitzungsraum, Ernst-Zermelo-Straße 1"}, { "$set": {"url": "https://www.openstreetmap.org/?mlat=48.00065\&mlon=7.84591\#map=19/48.00065/7.84591"}}, upsert = True)
raum.update_many({"gebaeude": gebaeude.find_one({"name_de": 'Fakultätssitzungsraum, <a href="https://www.openstreetmap.org/?mlat=48.00065\&mlon=7.84591\#map=19/48.00065/7.84591">Ernst-Zermelo-Straße 1</a>'})["_id"]}, { "$set": { "gebaeude": g["_id"]}})
gebaeude.delete_one({"name_de": 'Fakultätssitzungsraum, <a href="https://www.openstreetmap.org/?mlat=48.00065\&mlon=7.84591\#map=19/48.00065/7.84591">Ernst-Zermelo-Straße 1</a>'})
gebaeude.update_one({"name_de": '<a href="https://www.openstreetmap.org/?mlat=47.99252\&mlon=7.84775\#map=19/47.99252/7.84775">Breisacher Tor</a>'}, { "$set": {"name_de": "Breisacher Tor", "url": "https://www.openstreetmap.org/?mlat=47.99252\&mlon=7.84775\#map=19/47.99252/7.84775"}})
gebaeude.update_one({"name_de": "Ernst-Zermelo-Straße 1"}, {"$set": {"sichtbar": True}})
gebaeude.update_one({"name_de": "Hermann-Herder-Str. 10"}, {"$set": {"sichtbar": True}})


for v in ver.find():
    ver.update_one({"_id": v["_id"]}, {"$unset": {"kategorie": ""}})

for s in sem.find():
   sem.update_one({"_id": s["_id"]}, {"$unset": {"kategorie": ""}})



# Ab hier wird das Schema gecheckt
print("Check schema")
import schema
mongo_db.command("collMod", "semester", validator = schema.semester_validator, validationLevel='moderate')
mongo_db.command("collMod", "gebaeude", validator = schema.gebaeude_validator, validationLevel='moderate')
mongo_db.command("collMod", "raum", validator = schema.raum_validator, validationLevel='moderate')
mongo_db.command("collMod", "person", validator = schema.person_validator, validationLevel='moderate')
mongo_db.command("collMod", "anforderung", validator = schema.anforderung_validator, validationLevel='moderate')
mongo_db.command("collMod", "anforderungkategorie", validator = schema.anforderungkategorie_validator, validationLevel='moderate')
mongo_db.command("collMod", "rubrik", validator = schema.rubrik_validator, validationLevel='moderate')
mongo_db.command("collMod", "code", validator = schema.code_validator, validationLevel='moderate')
mongo_db.command("collMod", "studiengang", validator = schema.studiengang_validator, validationLevel='moderate')
mongo_db.command("collMod", "modul", validator = schema.modul_validator, validationLevel='moderate')
mongo_db.command("collMod", "veranstaltung", validator = schema.veranstaltung_validator, validationLevel='moderate')

