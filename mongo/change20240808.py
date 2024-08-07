from pymongo import MongoClient
import pandas as pd
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

planungkategorie = mongo_db["planungkategorie"]
planung = mongo_db["planung"]
person = mongo_db["person"]
planungkategorie.delete_many({})
planung.delete_many({})

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240808
mongo_db.command("collMod", "planungkategorie", validator = schema20240808.planungkategorie_validator, validationLevel='off')
mongo_db.command("collMod", "planung", validator = schema20240808.planung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")


df = pd.read_excel("planung.xlsx")
df = df.fillna("")

kats = list(set(df['Kategorie']))

i=0
for k in kats:
  i = i+1
  planungkategorie.insert_one({ "name": k, "kommentar": "", "rang": i })

planungkategorie.insert_one({ "name": "-", "kommentar": "", "rang": i+1 })

sems = ["2022SS",	"2022WS", "2023SS", "2023WS", "2024SS", "2024WS", "2025SS", "2025WS", "2026SS", "2026WS", "2027SS"]

for index, row in df.iterrows():
  x = {"name" : row["Veranstaltung"], "sws" : str(row["SWS"]), "semdozent" : [], "kommentar" : ""}  
  x["kategorie"] = planungkategorie.find_one({"name" : row["Kategorie"]})["_id"]
  for sem in sems:
    if row[sem] != "":
      y = list(person.find( {"name" : { "$in" : row[sem].split(",")}}))
      if y == []:
        print(f"Achtung bei {row[sem]}")
      x["semdozent"].append({ "sem" : sem, "dozent" : [ x["_id"] for x in y] , "kommentar" : ""} )
  planung.insert_one(x)
  
# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20240808
mongo_db.command("collMod", "planungkategorie", validator = schema20240808.planungkategorie_validator, validationLevel='moderate')
mongo_db.command("collMod", "planung", validator = schema20240808.planung_validator, validationLevel='moderate')
