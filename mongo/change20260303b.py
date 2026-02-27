from pymongo import MongoClient
import pandas as pd

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]
per = mongo_db["person"]
geb = mongo_db["gebaeude"]
ck = mongo_db["personencodekategorie"]
code = mongo_db["personencode"]

import schema20260303

mongo_db.command('collMod','person', validator=schema20260303.person_validator, validationLevel='off')

# abschluss, kommentar zur abwesenheit, kommentag_dekanat hinzufügen
# ck dekanat hinzufügen

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

per.update_many({}, { "$set" : { "hp_sichtbar" : True}})

print("Check schema")

mongo_db.command('collMod','person', validator=schema20260303.person_validator, validationLevel='moderate')

