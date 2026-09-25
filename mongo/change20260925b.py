from pymongo import MongoClient

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

import schema20260925b

# Neues Feld person.beisitz (required): Liste von {datum, anzahl}, chronologisch
# rückwärts sortiert. Wird in mi-person auf der Seite Personen_edit gepflegt.

collections = ["person"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

res = mongo_db["person"].update_many({"beisitz": {"$exists": False}}, {"$set": {"beisitz": []}})
print(f"person: beisitz bei {res.modified_count} Dokumenten ergänzt")

print("Setze Schema")

for name in collections:
    mongo_db.command('collMod', name, validator=getattr(schema20260925b, f"{name}_validator"), validationLevel='moderate')
    print(f"{name}: Validator gesetzt")
