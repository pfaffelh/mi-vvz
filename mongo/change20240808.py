# veranstaltung bekommt ein Feld "bearbeitet"
# Neue Collections planung und planungveranstaltung

from pymongo import MongoClient
import pandas as pd
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

planungkategorie = mongo_db["planungkategorie"]
planungveranstaltung = mongo_db["planungveranstaltung"]
planung = mongo_db["planung"]
person = mongo_db["person"]
veranstaltung = mongo_db["veranstaltung"]

planungkategorie.drop()
planung.drop()
planungveranstaltung.drop()

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240808
#mongo_db.command("collMod", "planungveranstaltung", validator = schema20240808.planungveranstaltung_validator, validationLevel='off')
#mongo_db.command("collMod", "planung", validator = schema20240808.planung_validator, validationLevel='off')

def get_regel(str):
  if str == "WS":
    res = "Jedes Wintersemester"
  elif str == "SS":
    res = "Jedes Sommersemester"
  else:
    res = "Jedes Semester"
  return res

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

df = pd.read_excel("planung.xlsx")
df = df.fillna("")

planungveranstaltung.insert_one({"name": "-", "sws" : "", "regel": "Jedes Semester", "rang" : 200, "kommentar": ""})

for v in list(veranstaltung.find()):
  veranstaltung.update_one({"_id" : v["_id"]}, { "$set" : {"bearbeitet": "Ersteintrag"}})  

sems = ["2022SS",	"2022WS", "2023SS", "2023WS", "2024SS", "2024WS", "2025SS", "2025WS", "2026SS", "2026WS", "2027SS"]

i=0
j=50
k=100
for index, row in df.iterrows():
  if row["Regel"] == "WS":
    i = i+1
    loc = i
  elif row["Regel"] == "SS":
    j = j+1
    loc = j
  else:
    k = k+1
    loc = k
  v = planungveranstaltung.insert_one({"name": row["Veranstaltung"], "sws" : str(row["SWS"]), "regel": get_regel(row["Regel"]), "rang" : loc, "kommentar": ""})
  for sem in sems:
    print(sem)
    if row[sem] != "":
      y = list(person.find( {"name" : { "$in" : row[sem].split(", ")}}))
      print([x["name"] for x in y])
      if y == []:
        print(f"Achtung bei {row[sem]}")
      planung.insert_one({ "veranstaltung" : v.inserted_id, "dozent" : [ x["_id"] for x in y], "kommentar" : "", "sem" : sem})
  
# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20240808
mongo_db.command("collMod", "planungveranstaltung", validator = schema20240808.planungveranstaltung_validator, validationLevel='moderate')
mongo_db.command("collMod", "planung", validator = schema20240808.planung_validator, validationLevel='moderate')
