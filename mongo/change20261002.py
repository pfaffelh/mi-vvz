from pymongo import MongoClient

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

import schema20261002

# Neue Felder person.namenszusatz_de und person.namenszusatz_en (required):
# Namenszusatz wie "von" oder "van der", deutsch und englisch. Wird in mi-person
# auf der Seite Personen_edit gepflegt.

collections = ["person"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

for feld in ["namenszusatz_de", "namenszusatz_en"]:
    res = mongo_db["person"].update_many({feld: {"$exists": False}}, {"$set": {feld: ""}})
    print(f"person: {feld} bei {res.modified_count} Dokumenten ergänzt")

print("Setze Schema")

for name in collections:
    mongo_db.command('collMod', name, validator=getattr(schema20261002, f"{name}_validator"), validationLevel='moderate')
    print(f"{name}: Validator gesetzt")
