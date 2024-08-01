from pymongo import MongoClient
import pymongo
import os
import datetime

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

dictionary = mongo_db["dictionary"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
# import schema20240801b
# mongo_db.command('collMod','veranstaltung', validator=schema20240801.veranstaltung_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

d = {
  "Assistent": "lecture assistant",
  "Belegung": "course registration",
  "Bewerbung": "application",
  "Einschreibung": "matriculation or enrolment",
  "Fachprüfungsausschuss": "Subject Examination Committee",
  "Fachprüfungsausschussvorsitzender": "Chairman/Chairwoman of the ...",
  "Fachschaft": "Student council",
  "Lehramt": "Teacher training",
  "Modul": "module",
  "Modulhandbuch": "Module handbook",
  "Orientierungsleistung": "orientation achievement",
  "Orientierungspraktikum": "orientation internship",
  "Pflichtmodul": "compulsory module",
  "Praktische Übung": "computer exercise tutorials",
  "Prüfungsamt": "Examination office",
  "Prüfungsabmeldung": "signing out of exams",
  "Prüfungsanmeldung": "registration of exams",
  "Prüfungsleistung": "graded examination",
  "Prüfungsordnung": "Examination regulations",
  "Prüfungsrücktritt": "withdrawal from an exam",
  "Studienberatung": "academic advise",
  "Studiengang": "Degree programme",
  "Studienleistung": "pass/fail assessment",
  "Vorlesung": "lecture",
  "Vorlesungsverzeichnis": "course catalogue",
  "Wahlmodul": "elective",
  "Weiterbildung": "Further education",
  "Übung": "exercise tutorials",
  "Zulassung": "admission",
  "Zwei-Hauptfächer Bachelor mit Lehramtsoption": "Two-Major Bachelor with Teaching Option"
}

for de, en in d.items():
    dictionary.insert_one({"de": de, "en": en, "kommentar": ""})

# Ab hier wird das Schema gecheckt
print("Check schema")
import schema20240801b
mongo_db.command("collMod", "dictionary", validator = schema20240801b.dictionary_validator, validationLevel='moderate')
