import os
import datetime
from pymongo import MongoClient, DESCENDING

# Create mongodump 
# os.system(f"mongodump --db vvz --archive=vvz_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}")

# Delete complete database
# os.system("mongo vvz --eval 'db.dropDatabase()'")

# Restore complete database
# Should be executed from mi-vvz/mongo/
# os.system(f"mongorestore --archive='vvz_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}'")  

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

sem = mongo_db["semester"]
gebaeude = mongo_db["gebaeude"]
raum = mongo_db["raum"]
cod = mongo_db["code"]
rub = mongo_db["rubrik"]
mod = mongo_db["modul"]
per = mongo_db["person"]
stu = mongo_db["studiengang"]
anf = mongo_db["anforderung"]
anfkat = mongo_db["anforderungkategorie"]
ver = mongo_db["veranstaltung"]
ter = mongo_db["terminart"]

#for v in list(ver.find()):
#    print("\n")
#    print(v["name_de"])
#    for t in v["woechentlicher_termin"]:
#        print(t["key"])
#        print(t["wochentag"])
#        x = ter.find_one({'_id': t["key"]})
#        if x:
#            print(x["name_de"])

rund = raum.find_one({"kurzname": "HsRundbau"})
weis = raum.find_one({"kurzname": "HsWeismann"})
hs2 = raum.find_one({"kurzname": "HSII"})
sr404 = raum.find_one({"kurzname": "SR404"})
sr125 = raum.find_one({"kurzname": "SR125"})
sr127 = raum.find_one({"kurzname": "SR127"})
sr226 = raum.find_one({"kurzname": "SR226"})
sr119 = raum.find_one({"kurzname": "SR119"})
sr218 = raum.find_one({"kurzname": "SR218"})
sr232 = raum.find_one({"kurzname": "R232"})
sr318 = raum.find_one({"kurzname": "SR318"})
sr403 = raum.find_one({"kurzname": "SR403"})
sr414 = raum.find_one({"kurzname": "SR414"})
hauptraum = [rund, weis, hs2, sr404, sr125, sr127, sr226]
print([r["_id"] for r in hauptraum])
