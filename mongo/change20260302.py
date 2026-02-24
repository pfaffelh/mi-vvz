from pymongo import MongoClient

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

per = mongo_db["person"]

import schema20260302

mongo_db.command('collMod','person', validator=schema20260302.person_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

per.update_many({}, { "$set" : { "gender" : "kA", "vorgesetzte" : [], "abwesend_start" : None, "abwesend_ende" : None}})

print("Check schema")
            

mongo_db.command('collMod','person', validator=schema20260302.person_validator, validationLevel='moderate')

