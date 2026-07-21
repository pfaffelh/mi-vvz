from pymongo import MongoClient

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

import schema20260721

# Feld "bearbeitet" (Wer hat wann zuletzt bearbeitet) in allen Collections einführen.
# person hatte das Feld schon; alle anderen bekommen es leer nachgezogen.
# dictionary hat keinen Validator, bekommt aber auch das Feld.

# Collections mit Validator
collections = ["anforderung", "anforderungkategorie", "code", "codekategorie",
               "gebaeude", "modul", "person", "personencode", "personencodekategorie",
               "planung", "planungveranstaltung", "raum", "rubrik", "semester",
               "studiengang", "terminart", "veranstaltung"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

for name in collections + ["dictionary"]:
    res = mongo_db[name].update_many({"bearbeitet": {"$exists": False}}, {"$set": {"bearbeitet": ""}})
    print(f"{name}: {res.modified_count} Dokumente ergänzt")

print("Setze Schema")

for name in collections:
    mongo_db.command('collMod', name, validator=getattr(schema20260721, f"{name}_validator"), validationLevel='moderate')
    print(f"{name}: Validator gesetzt")
