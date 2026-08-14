from pymongo import MongoClient

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

import schema20260813

# Neue Collection notiz: Die Notizen, die oben auf der Seite Dokumentation
# stehen. Ein Dokument pro Notiz, sortiert nach rang.
# Neue Collection hilfe: Die in der App geänderten help-Texte der Widgets.
# Enthält nur die vom Standard (util.HILFE) abweichenden Texte, key ist eindeutig.

collections = ["notiz", "hilfe"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

for name in collections:
    if name not in mongo_db.list_collection_names():
        mongo_db.create_collection(name)
        print(f"{name}: Collection angelegt")
    else:
        print(f"{name}: Collection existiert bereits")

mongo_db["hilfe"].create_index("key", unique=True)
print("hilfe: eindeutiger Index auf key gesetzt")

print("Setze Schema")

for name in collections:
    mongo_db.command('collMod', name, validator=getattr(schema20260813, f"{name}_validator"), validationLevel='moderate')
    print(f"{name}: Validator gesetzt")
