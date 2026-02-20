from pymongo import MongoClient
import json

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

per = mongo_db["person"]
geb = mongo_db["gebaeude"]
ck = mongo_db["personencodekategorie"]
code = mongo_db["personencode"]

import schema20260301


mongo_db.command('collMod','person', validator=schema20260301.person_validator, validationLevel='off')
if "personencode" in mongo_db.list_collection_names():
    mongo_db.command('collMod','personencode', validator=schema20260301.personencode_validator, validationLevel='off')
if "personencodekateorie" in mongo_db.list_collection_names():
    mongo_db.command('collMod','personencodekategorie', validator=schema20260301.personencodekategorie_validator, validationLevel='off')

j = 0

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

########### 
## dummy ##
########### 

if not ck.find_one({"beschreibung_de" : "dummy-Codekategorie"}):
    ck.insert_one(
        {"name_de" : "-", 
        "name_en" : "-", 
        "beschreibung_de" : "dummy-Codekategorie", 
        "beschreibung_en" : "", 
        "kommentar" : "", 
        "rang": 10
        })

##################
#### Sprachen ####
##################

sprachen = [
    {"name" : "de", "beschreibung_de": "Deutsch", "beschreibung_en" : "German"}, 
    {"name" : "en", "beschreibung_de": "Englisch", "beschreibung_en" : "English"}
]

if not ck.find_one({"name_de" : "Sprache"}):
    new_ck = ck.insert_one(
        {"name_de" : "Sprache", 
        "name_en" : "Language", 
        "beschreibung_de" : "Sprachkenntnisse, insbesondere für Lehre", 
        "beschreibung_en" : "", 
        "kommentar" : "", 
        "rang": 2
        })
    for s in sprachen:
        c = {"codekategorie" : new_ck.inserted_id,
            "kommentar" : "",
            "kommentar_html" : "", 
            "rang" : j
            }
        j = j + 1
        c = code.insert_one(s | c)


#####################
#### Abteilungen ####
#####################
abteilungen = [
    {"name" : "D", "beschreibung_de": "Dekanat", "beschreibung_en" : "Dean's office"}, 
    {"name" : "PA", "beschreibung_de": "Prüfungsamt", "beschreibung_en" : ""},
    {"name" : "RM", "beschreibung_de": "Abteilung für Reine Mathematik", "beschreibung_en" : "Department of Pure Mathematics"}, 
    {"name" : "AM", "beschreibung_de": "Abteilung für Angewandte Mathematik", "beschreibung_en" : "Department of Applied Mathematics"}, 
    {"name" : "ML", "beschreibung_de": "Abteilung für Mathematische Logik", "beschreibung_en" : "Department of Logic"}, 
    {"name" : "MSt", "beschreibung_de": "Abteilung für Stochastik", "beschreibung_en" : "Department of Probability Theory"}, 
    {"name" : "Di", "beschreibung_de": "Abteilung für Didaktik der Mathematik", "beschreibung_en" : "Department of Didactics of Mathematics"}
]

# "required": ["name_de", "name_en", "beschreibung_de", "beschreibung_en", "rang", "code", "kommentar_html", "kommentar"],
if not ck.find_one({"name_de" : "Abteilung"}):

    abt = {}
    new_ck = ck.insert_one(
        {
            "name_de" : "Abteilung", 
            "name_en" : "Department", 
            "beschreibung_de" : "Zugehörigkeit zu einer Abteilung", 
            "beschreibung_en" : "", 
            "kommentar" : "", 
            "rang": 0
        })

    j = 0
    for a in abteilungen:
        c = {"codekategorie" : new_ck.inserted_id,
            "kommentar" : "",
            "kommentar_html" : "", 
            "rang" : j
            }
        j = j + 1
        c = code.insert_one(a | c)
        abt[a["name"]] = c.inserted_id
    # abt["RM"] ist die id des Codes

#######################
#### Statusgruppen ####
#######################

statusgruppen = [
    {"name" : "faculty", "beschreibung_de": "Professorinnen und Professoren", "beschreibung_en" : "Professors"}, 
    {"name" : "retired", "beschreibung_de": "Emeritierte und pensionierte Professoren", "beschreibung_en" : "Retired Professors"}, 
    {"name" : "secretary", "beschreibung_de": "Sekretariate", "beschreibung_en" : "Administration"}, 
    {"name" : "employee", "beschreibung_de": "Administration und Technik", "beschreibung_en" : "Technical employees"}, 
    {"name" : "staff", "beschreibung_de": "Wissenschaftlicher Dienst", "beschreibung_en" : "Scientists"}, 
    {"name" : "student", "beschreibung_de": "Studenten", "beschreibung_en" : "Students"}, 
]

if not ck.find_one({"name_de" : "Statusgruppe"}):
    status={}
    new_ck = ck.insert_one(
        {
            "name_de" : "Statusgruppe", 
            "name_en" : "", 
            "beschreibung_de" : "Zugehörigkeit zu einer Statustgruppe", 
            "beschreibung_en" : "", 
            "kommentar" : "", 
            "rang": 1
        })
    for s in statusgruppen:
        c = {"codekategorie" : new_ck.inserted_id,
            "kommentar" : "",
            "kommentar_html" : "", 
            "rang" : j
            }
        j = j + 1
        c = code.insert_one(s | c)
        status[s["name"]] = c.inserted_id
        # status["staff"] ist die id des Codes

##################
#### Personen ####
##################

# "required": ["name", "name_en", "vorname", "name_prefix", "titel", "kennung", "rang", "tel1", "email1", "raum1", "gebaeude1", "tel2", "email2", "raum2", "gebaeude2", "sichtbar", "hp_sichtbar", "einstiegsdatum", "ausstiegsdatum", "semester", "veranstaltung", "kommentar_html", "kommentar", "bearbeitet"],
# neu sind kennung, einstiegsdatum, ausstiegsdateum, lehrperson, raum, gebaude, code

# street
E1 = geb.find_one({"name_de" : "Ernst-Zermelo-Str. 1"})["_id"]
HH10 = geb.find_one({"name_de" : "Hermann-Herder-Str. 10"})["_id"]
l = geb.find_one({"name_de": "-"})["_id"]

# Erstmal sollen alle Felder angelegt werden:
for p in list(per.find({})):
    per.update_one({"_id" : p["_id"]}, { "$set" : 
                {
                    "kennung" : "", 
                    "lehrperson" : False, 
                    "raum1" : "", 
                    "gebaeude1": l, 
                    "raum2" : "", 
                    "gebaeude2": l, 
                    "email1" : p["email"], 
                    "tel1": "", 
                    "email2" : "", 
                    "tel2": "", 
                    "einstiegsdatum" : None, 
                    "ausstiegsdatum" : None,
                    "ldap" : False,
                    "code" : [],
                    "kommentar_html" : "",
                    "bearbeitet" : "Initialer Eintrag."
                }})

print("Check schema")
            

mongo_db.command('collMod','person', validator=schema20260301.person_validator, validationLevel='moderate')
mongo_db.command('collMod','personencode', validator=schema20260301.personencode_validator, validationLevel='moderate')
mongo_db.command('collMod','personencodekategorie', validator=schema20260301.personencodekategorie_validator, validationLevel='moderate')

