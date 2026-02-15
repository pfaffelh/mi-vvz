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
mongo_db.command('collMod','personencode', validator=schema20260301.personencode_validator, validationLevel='off')
mongo_db.command('collMod','personencodekategorie', validator=schema20260301.personencodekategorie_validator, validationLevel='off')

j = 0

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

##################
#### Sprachen ####
##################

sprachen = [
    {"name" : "de", "beschreibung_de": "Deutsch", "beschreibung_en" : "German"}, 
    {"name" : "en", "beschreibung_de": "Englisch", "beschreibung_en" : "English"}
]

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
        "rang" : j
        }
    j = j + 1
    c = code.insert_one(s | c)


#####################
#### Abteilungen ####
#####################
abteilungen = [
    {"name" : "RM", "beschreibung_de": "Abteliung für Reine Mathematik", "beschreibung_en" : "Department of Pure Mathematics"}, 
    {"name" : "AM", "beschreibung_de": "Abteliung für Angewandte Mathematik", "beschreibung_en" : "Department of Applied Mathematics"}, 
    {"name" : "ML", "beschreibung_de": "Abteliung für Mathematische Logik", "beschreibung_en" : "Department of Logic"}, 
    {"name" : "MSt", "beschreibung_de": "Abteliung für Stochastik", "beschreibung_en" : "Department of Probability Theory"}, 
    {"name" : "Did", "beschreibung_de": "Abteilung für Didaktik der Mathematik", "beschreibung_en" : "Department of Didactics of Mathematics"}
]

# "required": ["name_de", "name_en", "beschreibung_de", "beschreibung_en", "rang", "code", "kommentar"],
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
        "rang" : j
        }
    j = j + 1
    c = code.insert_one(s | c)
    status[s["name"]] = c.inserted_id
    # status["staff"] ist die id des Codes

##################
#### Personen ####
##################

# "required": ["name", "name_en", "vorname", "name_prefix", "titel", "kennung", "rang", "tel", "email", "raum", "gebaeude", "sichtbar", "hp_sichtbar", "lehrperson", "einstiegsdatum", "ausstiegsdatum", "semester", "veranstaltung", "kommentar"],
# neu sind kennung, einstiegsdatum, ausstiegsdateum, lehrperson, raum, gebaude, code

# street
E1 = geb.find_one({"name_de" : "Ernst-Zermelo-Str. 1"})["_id"]
HH10 = geb.find_one({"name_de" : "Hermann-Herder-Str. 10"})["_id"]

# Erstmal sollen alle Felder angelegt werden:
per.update_many({}, { "$set" : 
                {
                    "kennung" : "", 
                    "lehrperson" : False, 
                    "raum" : "", 
                    "gebaeude": E1, 
                    "einstiegsdatum" : None, 
                    "ausstiegsdatum" : None,
                    "ldap" : False,
                    "code" : []
                }})


with open('ldap.json', 'r') as json_file:
    data = json.load(json_file)


# ou -> abteilung
# eduPersonAffiliation -> status

for item in data:
    print(item)
    if item["givenName"] != None and item["sn"] != None:
        if per.find_one({"vorname" : item.get("givenName"), "name" : item.get("sn")}):
            per.update_one(
                {
                    "vorname" : item.get("givenName"),
                    "name" : item.get("sn")
                }, 
                {
                    "$set" : 
                        { 
                            "raum" : item.get("roomNumber", ""),
                            "url" : item.get("labeledURI", ""), 
                            "email" : item.get("mail", ""),
                            "titel": item.get("personalTitle") if item.get("personalTitle") not in [None, "M.Sc.", "MSc.", "M.Sc. ", "Dipl.-Math.", "B.A.", "Dipl.-Math."] else "",
                            "tel" : f"+49 761 - 203 {item.get('telephoneNumber')}" if item.get('telephoneNumber') is not None else "",
                            "ldap" : True
                        }
                })
        else:
#        "required": ["name", "name_en", "vorname", "name_prefix", "titel", "kennung", "rang", "tel", "email", "raum", "gebaeude", "sichtbar", "hp_sichtbar", "lehrperson", "einstiegsdatum", "ausstiegsdatum", "semester", "code", "veranstaltung", "kommentar"],
            per.insert_one(
                {
                    "name" : item.get("sn"),
                    "name_en" : "",
                    "vorname" : item.get("givenName"),
                    "name_prefix" : "",
                    "titel": item.get("personalTitle") if item.get("personalTitle") not in [None, "M.Sc.", "MSc.", "M.Sc. ", "Dipl.-Math.", "B.A.", "Dipl.-Math."] else "",
                    "kennung" : "", 
                    "rang" : 200 + j,
                    "tel" : f"+49 761 - 203 {item.get('telephoneNumber')}" if item.get('telephoneNumber') is not None else "",
                    "email" : item.get("mail") if item.get("mail") is not None else "",
                    "raum" : item.get("roomNumber", ""),
                    "gebaeude": E1, 
                    "url" : item.get("labeledURI", ""),
                    "sichtbar" : False,
                    "hp_sichtbar" : False,
                    "ldap" : True,
                    "einstiegsdatum" : None, 
                    "ausstiegsdatum" : None,
                    "semester" : [],
                    "code" : [], 
                    "veranstaltung" : [],
                    "kommentar" : "",                    
                })
            j = j + 1
        if item.get("street") in ["E1", "HH10"]:
            per.update_one(
                {
                    "vorname" : item["givenName"], 
                    "name" : item["sn"]
                }, 
                {
                    "$set" : 
                    {
                        "gebaeude" : E1 if item.get("street") == "E1" else HH10
                    }
                }
            )
        if item.get("ou") in [a["name"] for a in abteilungen]:
            per.update_one(
                {
                    "vorname" : item["givenName"], 
                    "name" : item["sn"]
                }, 
                {
                    "$push" : {
                        "code" : abt[item.get("ou")]
                    }
                }
            )
        aff = [item.get("eduPersonPrimaryAffiliation")] + (item.get("eduPersonAffiliation") if isinstance(item.get("eduPersonAffiliation"), list) else [item.get("eduPersonAffiliation")])
        for s in [s["name"] for s in statusgruppen]:
            if s in aff:
                per.update_one(
                    {
                        "vorname" : item["givenName"], 
                        "name" : item["sn"]
                    }, 
                    {   
                        "$set" : {
                            # lehrpersonen sind staff, faculty
                            "lehrperson" : True if s in ["staff", "faculty"] else False
                        },                    
                        "$push" : {
                            "code" : status[s]
                        }
                    }
                )

print("Check schema")
            

mongo_db.command('collMod','person', validator=schema20260301.person_validator, validationLevel='moderate')
mongo_db.command('collMod','personencode', validator=schema20260301.personencode_validator, validationLevel='moderate')
mongo_db.command('collMod','personencodekategorie', validator=schema20260301.personencodekategorie_validator, validationLevel='moderate')

