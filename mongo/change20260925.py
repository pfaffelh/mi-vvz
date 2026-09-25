from pymongo import MongoClient

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

import schema20260925

# Der Validator von planung war noch der Entwurf von 2024/10 (name, kategorie,
# sws, semdozent). Mit change20260721 wurde er erstmals gesetzt, seitdem
# scheitert das Anlegen neuer Planungen. Jetzt passt er zu den Dokumenten
# (veranstaltung, sem, dozent, kommentar, bearbeitet).

collections = ["planung"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

print("Setze Schema")

for name in collections:
    mongo_db.command('collMod', name, validator=getattr(schema20260925, f"{name}_validator"), validationLevel='moderate')
    print(f"{name}: Validator gesetzt")
