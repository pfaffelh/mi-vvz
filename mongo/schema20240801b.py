from pymongo import MongoClient

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

# collections sind:

# dictionary
# gebauede
# raum
# semester 
# rubrik
# person
# code 
# studiengang
# modul
# anforderung
# anforderungkategorie
# veranstaltung

# dictionary: Kleines Lexikon zur Übersetzung deutsch-englisch, für FachbegriffeGebäudes
dictionary_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Paar aus deutschen und englischen Begriffen.",
        "required": ["de", "en", "kommentar"],
        "properties": {
            "de": {
                "bsonType": "string",
                "description": "Der deutsche Begriff -- required"
            },
            "en": {
                "bsonType": "string",
                "description": "Der englische Begriff -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Begriff."
            }
        }
    }
}

# gebaeude: Beschreibung eines Gebäudes
gebaeude_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung eines Gebäudes, also vor allem seiner Adresse.",
        "required": ["name_de", "name_en", "kurzname", "adresse", "url", "rang", "sichtbar", "kommentar"],
        "properties": {
            "name_de": {
                "bsonType": "string",
                "description": "Der deutsche Name für das Gebäude, zB Ernst-Zermelo-Str. 1 -- required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Der englische Name für das Gebäude, zB Ernst-Zermelo-Str. 1"
            },
            "kurzname": {
                "bsonType": "string",
                "description": "Kurzname für das Gebäude"
            },
            "adresse": {
                "bsonType": "string",
                "description": "Adresse des Gebäudes."
            },
            "url": {
                "bsonType": "string",
                "description": "Webpage für dieses Gebäude (zB OpenStreetmap)."
            },
            "rang": {
                "bsonType": "int",
                "description": "Bestimmt, an welcher Stelle das Gebäude in Auswahlmenüs angezeigt werden soll. "
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "Bestimmt, pb das Gebäude in Auswahlmenüs angezeigt werden soll. "
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Gebäude."
            }
        }
    }
}

# raum: Beschreibung von Räumen, also zB SR125
raum_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung von Räumen, also zB Hörsälen.",
        "required": ["name_de", "name_en", "kurzname", "gebaeude", "raum", "groesse", "rang", "sichtbar", "kommentar"],
        "properties": {
            "name_de": {
                "bsonType": "string",
                "description": "must be a string -- required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Name des Raums"
            },
            "kurzname": {
                "bsonType": "string",
                "description": "Kurzname für den Raum"
            },
            "gebaeude": {
                "bsonType": "objectId",
                "description": "Die Gebäude-id1 des Gebäudes, in dem sich der Raum befindet."
            },
            "raum": {
                "bsonType": "string",
                "description": "Raumnummer, in dem sich der Raum befindet."
            },
            "groesse": {
                "bsonType": "int",
                "description": "Maximale Anzahl der Teilnehmer für diesen Raum."
            },
            "rang": {
                "bsonType": "int",
                "description": "Bestimmt, an welcher Stelle der Raum in Auswahlmenüs angezeigt werden soll. "
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "Bestimmt, ob der Raum in Auswahlmenüs angezeigt werden soll. "
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zu diesem Raum."
            },
        }
    }
}

# person: Beschreibung einer Person
person_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Person",
        "description": "Soll auch noch alle Informationen für das Personenverzeichnis bekommen.",
        "required": ["name", "vorname", "name_prefix", "titel", "rang", "tel", "email", "sichtbar", "hp_sichtbar", "semester", "veranstaltung"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "Nachname der Person"
            },
            "vorname": {
                "bsonType": "string",
                "description": "Vorname der Person."
            },
            "name_prefix": {
                "bsonType": "string",
                "description": "Abkürzung des Vornamen der Person."
            },
            "titel": {
                "bsonType": "string",
                "description": "Titel der Person"
            },
            "rang": {
                "bsonType": "int",
                "description": "Rang, nach dem (absteigend) sortiert wird."
            },
            "tel": {
                "bsonType": "string",
                "description": "Telefonnummer der Person"
            },
            "email": {
                "bsonType": "string",
                "description": "Email-Adresse der Person"
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Person in Auswahlmenüs sichtbar sein soll."
            },
            "hp_sichtbar": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Person auf Webpage etc sichtbar sein soll."
            },
            "semester": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "eine Semester-id."
                }
            },
            "veranstaltung": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "Kurs, der der Person zugeordnet ist."
                }
            }
        }
    }
}

# # group: Beschreibung einer Gruppe von Personen, zB "Abteilung für Mathematische Logik"
# # A person can belong to arbitrarily many groups.
# group_validator = {
#     "$jsonSchema": {
#         "bsonType": "object",
#         "title": "Beschreibung einer Gruppe von Personen, zB in Abteilungen",
#         "required": ["name", "id"],
#         "properties": {
#             "name": {
#                 "bsonType": "string",
#                 "description": "Name der Gruppe -- required"
#             },
#             "id": {
#                 "bsonType": "string",
#                 "description": "Identifier der Gruppe -- required"
#             },
#             "shortname": {
#                 "bsonType": "string",
#                 "description": "Kurzname der Gruppe."
#             },
#             "persons": {
#                 "bsonType": "array",
#                 "items": {
#                     "bsonType": "string",
#                     "description": "Person, der der Gruppe zugeordnet ist."
#                 }
#             },
#             "comment": {
#                 "bsonType": "string",
#                 "description": "Kommentar."
#             },
#         }
#     }
# }

# semester: Beschreibung eines Semesters
semester_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung eines Semesters",
        "description": "Enthält auch alle courses.",
        "required": ["name_de", "name_en", "kurzname", "rang", "rubrik", "code", "veranstaltung", "hp_sichtbar"],
        "properties": {
            "name_de": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "must be a string"
            },
            "kurzname": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "rang": {
                "bsonType": "int",
                "description": "Rang, nach dem (absteigend) sortiert wird."
            },
            "hp_sichtbar": {
                "bsonType": "bool",
                "description": "bestimmt, ob das Semester auf der Homepage angezeigt werden soll."
            },
            "prefix_de": {
                "bsonType": "string",
                "description": "To start the vvz on math..."
            },
            "prefix_en": {
                "bsonType": "string",
                "description": "To start the vvz on math..."
            },
            "rubrik": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "must be an _id from the rubrik collection"
                }
            },
            "code": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "must be an _id from the code collection"
                }
            },
            "veranstaltung": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "must be an _id from the course collection"
                }
            }
        }
    }
}

# rubrik: Klassifizierung von Veranstaltungen, zB "Vorlesungen"
rubrik_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung der rubrik einer Veranstaltung, zB Proseminar.",
        "required": ["titel_de", "titel_en", "untertitel_de", "untertitel_en", "rang", "semester", "prefix_de", "prefix_en", "suffix_de", "suffix_en", "veranstaltung", "kommentar"],
        "properties": {
            "titel_de": {
                "bsonType": "string",
                "description": "Langname der rubrik -- required"
            },
            "titel_en": {
                "bsonType": "string",
                "description": "Langname der rubrik -- required"
            },
            "untertitel_de": {
                "bsonType": "string",
                "description": "Langname der rubrik -- required"
            },
            "untertitel_en": {
                "bsonType": "string",
                "description": "Langname der rubrik -- required"
            },
            "semester": {
                "bsonType": "objectId",
                "description": "Die _id des Semesters, für das diese Category gilt."
            },
            "hp_sichtbar": {
                "bsonType": "bool",
                "description": "Bestimmt, ob die rubrik auf der Homepage sichtbar ist."
            },
            "prefix_de": {
                "bsonType": "string",
                "description": "Gibt an, was bei Anzeigen vor dieser rubrik angezeigt wird. Wenn etwa vor '1a. Einführende Vorlesungen' noch 'Vorlesungen' angezeigt werden soll, steht hier 'Vorlesungen'."
            },
            "prefix_en": {
                "bsonType": "string",
                "description": "Gibt an, was bei Anzeigen vor dieser rubrik angezeigt wird. Wenn etwa vor '1a. Einführende Vorlesungen' noch 'Vorlesungen' angezeigt werden soll, steht hier 'Vorlesungen'."
            },
            "suffix_de": {
                "bsonType": "string",
                "description": "Gibt an, was bei Anzeigen nach derÜberschrift dieser rubrik angezeigt wird. Wenn etwa nach '1a. Einführende Vorlesungen' noch ein erklärender Text stehen soll, steht dieser hier."
            },
            "suffix_en": {
                "bsonType": "string",
                "description": "Gibt an, was bei Anzeigen vor dieser rubrik angezeigt wird. Wenn etwa vor '1a. Einführende Vorlesungen' noch 'Vorlesungen' angezeigt werden soll, steht hier 'Vorlesungen'."
            },
            "rang": {
                "bsonType": "int",
                "description": "Rang, nach dem (aufsteigend) sortiert wird."
            },
            "veranstaltung": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "must be an _id from the course collection"
                }
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Kürzel"
            }
        }
    }
}

# # person_category: Klassifizierung von Personen, zB Dozenten
# # A person only belongs to a single person_category.
# person_category_validator = {
#     "$jsonSchema": {
#         "bsonType": "object",
#         "title": "Beschreibung der rubrik einer Person, zB Dozent.",
#         "required": ["name", "id", "shortname"],
#         "properties": {
#             "name": {
#                 "bsonType": "string",
#                 "description": "Langname der rubrik -- required"
#             },
#             "id": {
#                 "bsonType": "string",
#                 "description": "Identifier der rubrik."
#             },
#             "shortname": {
#                 "bsonType": "string",
#                 "description": "Kurzname der rubrik."
#             },
#             "rang": {
#                 "bsonType": "int",
#                 "description": "Rang, nachdem (aufsteigend) die Darstellung sortiert wird."
#             },
#             "kommentar": {
#                 "bsonType": "string",
#                 "description": "Kommentar"
#             }
#         }
#     }
# }

# code: Kürzel für die Webpage, zB B, W, II, III etc
code_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung der Codes, die auf der Webpage verwendet werden",
        "required": ["name", "codekategorie", "semester", "beschreibung_de", "beschreibung_en", "rang", "kommentar", "veranstaltung"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "Das Kürzel des Codes, B, W, ... -- required"
            },
            "codekategorie": {
                "bsonType": "objectId",
                "description": "Bestimmt, zu welcher Kategorie ein Code passt."
            },
            "semester": {
                "bsonType": "objectId",
                "description": "Die _id für das Semester, für das dieser Code gilt -- required"
            },
            "beschreibung_de": {
                "bsonType": "string",
                "description": "Beschreibung des Kürzels"
            },
            "beschreibung_en": {
                "bsonType": "string",
                "description": "Beschreibung des Kürzels"
            },
            "rang": {
                "bsonType": "int",
                "description": "Rang, nach dem (aufsteigend) sortiert wird."
            },
            "veranstaltung": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "Ein _id aus den Veranstlatungen."
                }
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Kürzel"
            }
        }
    }
}

# code: Kürzel für die Webpage, zB B, W, II, III etc
codekategorie_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung der Kategorie eines Codes (zB Sprache), die für die Beschreibung einer Veranstaltung verwendet wird.",
        "required": ["name_de", "name_en", "hp_sichtbar", "komm_sichtbar", "beschreibung_de", "beschreibung_en", "rang", "semester", "code", "kommentar"],
        "properties": {
            "name_de": {
                "bsonType": "string",
                "description": "Die Beschreibung der Kategorie, zB Sprache, Evaluation,... -- required"
            },
            "name_de": {
                "bsonType": "string",
                "description": "Die Beschreibung der Kategorie, zB Sprache, Evaluation,... -- required"
            },
            "hp_sichtbar": {
                "bsonType": "bool",
                "description": "Bestimmt, ob diese Kategorie auf der Homepage sichtbar ist."
            },
            "komm_sichtbar": {
                "bsonType": "bool",
                "description": "Bestimmt, ob diese Kategorie in den Kommentaren sichtbar ist."
            },
            "beschreibung_de": {
                "bsonType": "string",
                "description": "Beschreibung des Kürzels"
            },
            "beschreibung_en": {
                "bsonType": "string",
                "description": "Beschreibung des Kürzels"
            },
            "rang": {
                "bsonType": "int",
                "description": "Rang, nach dem (aufsteigend) sortiert wird."
            },
            "semester": {
                "bsonType": "objectId",
                "description": "Die _id für das Semester, für das diese Codekategorie gilt -- required"
            },
            "code": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "Ein _id aus den Codes."
                }
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zur Codekategorie"
            }
        }
    }
}

# studiengang: Studiengang
studiengang_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung von Studiengängen",
        "description": "Enthält vor allem eine Liste von Modulen, die zu absolvieren sind.",
        "required": ["name", "kurzname", "rang", "modul", "kommentar", "sichtbar"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "Name des Studiengangs -- required"
            },
            "kurzname": {
                "bsonType": "string",
                "description": "Kurzname des Studiengangs -- required"
            },
            "rang": {
                "bsonType": "int",
                "description": "Wird nur angezeigt, wenn True"
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "Wird nur angezeigt, wenn True"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Wird nur angezeigt, wenn True"
            },
            "modul": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "must be an _id from the modul collection"
                }
            }
        }
    }
}

# modul: Modul
modul_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung eines Moduls",
        "description": "",
        "required": ["name_de", "name_en", "kurzname", "studiengang", "sichtbar", "kommentar", "rang"],
        "properties": {
            "name_de": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "kurzname": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "studiengang": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "must be an _id from the studiengang collection"
                }
            },
            "rang": {
                "bsonType": "int",
                "description": "Wird nur angezeigt, wenn True"
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "bestimmt, ob das Modul in Auswahlmenüs angezeigt wird."
            },
            "kommentar": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
        }
    }
}

# anforderungskategorie: Kategorie einer Anforderung
anforderungkategorie_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Kategorie einer Anforderung (zB PL oder SL für Prüfungs- und Studienleistung.).",
        "required": ["name_de", "name_en", "rang", "sichtbar", "kommentar"],
        "properties": {
            "name_de": {
                "bsonType": "string",
                "description": "Der deutsche Name für die Kategorie"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Der englische Name für die Kategorie"
            },
            "rang": {
                "bsonType": "int",
                "description": "Bestimmt, an welcher Stelle die Kategorie angezeigt werden soll. "
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "Bestimmt, ob die Kategorie in Auswahlmenüs angezeigt werden soll. "
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zur Kategorie."
            }
        }
    }
}

# anforderung: eine Anforderung
anforderung_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Anforderung (zB Mündliche Prüfung, 30 Minuten.).",
        "required": ["name_de", "name_en", "anforderungskategorie", "rang", "sichtbar", "kommentar"],
        "properties": {
            "name_de": {
                "bsonType": "string",
                "description": "Der deutsche Name für die Anforderung"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Der englische Name für die Anforderung"
            },
            "anforderungskategorie": {
                "bsonType": "objectId",
                "description": "Eine _id für eine Anforderungskategorie. "
            },
            "rang": {
                "bsonType": "int",
                "description": "Bestimmt, an welcher Stelle die Anforderung angezeigt werden soll. "
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "Bestimmt, ob die Anforderung in Auswahlmenüs angezeigt werden soll. "
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zur Kategorie."
            }
        }
    }
}

# veranstaltung: Beschreibung einer Veranstaltung
veranstaltung_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Veranstaltung",
        "description": "Hier werden alle Daten einer Veranstaltung hinterlegt, die sowohl für das Modulhandbuch, als auch für die Webpage benötigt werden.",
        "required": ["name_de", "name_en", "midname_de", "midname_en", "kurzname", "rubrik", "code", "rang", "semester", "ects", "url", "inhalt_de", "inhalt_en", "literatur_de", "literatur_en", "vorkenntnisse_de", "vorkenntnisse_en", "kommentar_latex_de", "kommentar_latex_en", "verwendbarkeit_modul", "verwendbarkeit_anforderung", "verwendbarkeit", "dozent", "assistent", "organisation", "woechentlicher_termin", "einmaliger_termin", "kommentar_html_de", "kommentar_html_en", "hp_sichtbar"],
        "properties": {
            "hp_sichtbar": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Person auf Webpage etc sichtbar sein soll."
            },
            "name_de": {
                "bsonType": "string",
                "description": "Voller Name der Veranstaltung (de)"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Voller Name der Veranstaltung (en)"
            },
            "midname_de": {
                "bsonType": "string",
                "description": "Etwas abgekürzte Version des Namens."
            },
            "midname_en": {
                "bsonType": "string",
                "description": "Etwas abgekürzte Version des Namens."
            },
            "kurzname": {
                "bsonType": "string",
                "description": "Kürzel der Veranstaltung"
            },
            "rubrik": {
                "bsonType": "objectId",
                "description": "rubrik-id der Veranstaltung"
            },
            "code": {
                "bsonType": "array",
                "description": "Codes für die Veranstaltung (für die Webpage).",
                "items": {
                    "bsonType": "objectId",
                    "description": "Die _id eines Codes."
                }
            },
            "rang": {
                "bsonType": "int",
                "description": "Rang, nachdem (aufsteigend) die Darstellung sortiert wird."
            },
            "semester": {
                "bsonType": "objectId",
                "description": "_id des Semesters, in der die Veranstaltung abgehalten wird."
            },
            "ects": {
                "bsonType": "string",
                "description": "Typische ECTS-Punktzahl, die bei erfolgreicher Belegung verbucht werden."
            },
            "url": {
                "bsonType": "string",
                "description": "Webpage der Veranstaltung."
            },
            "inhalt_de": {
                "bsonType": "string",
                "description": "Inhalt der Veranstaltung, für das kommentierte Vorlesungsverzeichnis. Darf LaTeX-Code enthalten."
            },
            "inhalt_en": {
                "bsonType": "string",
                "description": "Inhalt der Veranstaltung, für das kommentierte Vorlesungsverzeichnis. Darf LaTeX-Code enthalten."
            },
            "literatur_de": {
                "bsonType": "string",
                "description": "Literatur für die Veranstaltung, für das kommentierte Vorlesungsverzeichnis (de). Darf LaTeX-Code enthalten."
            },
            "literatur_en": {
                "bsonType": "string",
                "description": "Literatur für die Veranstaltung, für das kommentierte Vorlesungsverzeichnis (en). Darf LaTeX-Code enthalten."
            },
            "vorkenntnisse_de": {
                "bsonType": "string",
                "description": "Vorkenntnisse für die Veranstaltung, für das kommentierte Vorlesungsverzeichnis (de). Darf LaTeX-Code enthalten."
            },
            "vorkenntnisse_en": {
                "bsonType": "string",
                "description": "Vorkenntnisse für die Veranstaltung, für das kommentierte Vorlesungsverzeichnis (en). Darf LaTeX-Code enthalten."
            },
            "kommentar_latex_de": {
                "bsonType": "string",
                "description": "Kommentar für das kommentierte Vorlesungsverzeichnis."
            },
            "kommentar_latex_en": {
                "bsonType": "string",
                "description": "Kommentar für das kommentierte Vorlesungsverzeichnis."
            },
            "verwendbarkeit_modul": {
                "bsonType": "array",
                "description": "_ids für die Module, in denen die Veranstaltung verwendet werden kann.",
                "items": {
                    "bsonType": "objectId",
                    "description": "Die _id eines Module."
                }
            },
            "verwendbarkeit_anforderung": {
                "bsonType": "array",
                "description": "_ids für die Anforderungen, die in der Veranstaltung erbracht werden können.",
                "items": {
                    "bsonType": "objectId",
                    "description": "Die _id einer Anforderung."
                }
            },
            "verwendbarkeit": {
                "bsonType": "array",
                "description": "Liste der Verwendbarkeiten für die Veranstaltung.",
                "items": {
                    "bsonType": "object",
                    "description": "Beschreibung einer Verwendbarkeit",
                    "required": ["modul", "anforderung"],
                    "properties": {
                        "modul": {
                            "bsonType": "objectId",
                            "description": "_id eines Moduls, in dem die Veranstaltung verwendet wird."
                        },
                        "anforderung": {
                            "bsonType": "objectId",
                            "description": "Eine Anforderungs-_id.",
                        },
                    }
                }
            },
            "dozent": {
                "bsonType": "array",
                "description": "Liste aller an der Veranstaltung beteiligten Dozenten.",
                "items": {
                    "bsonType": "objectId",
                    "description": "_id einer Person."
                }
            },
            "assistent": {
                "bsonType": "array",
                "description": "Liste aller an der Veranstaltung beteiligten Assistenten.",
                "items": {
                    "bsonType": "objectId",
                    "description": "_id einer Person."
                }
            },
            "organisation": {
                "bsonType": "array",
                "description": "Liste aller an der Veranstaltung beteiligten Organisatoren.",
                "items": {
                    "bsonType": "objectId",
                    "description": "_id einer Person."
                }
            },
            "woechentlicher_termin": {
                "bsonType": "array",
                "description": "Wöchentliche Termine der Veranstaltung.",
                "items": {
                    "bsonType": "object",
                    "description": "Beschreibung des Termins.",
                    "required": ["key", "raum", "person", "wochentag", "start", "ende", "kommentar_de", "kommentar_en"],
                    "properties": {
                        "key": {
                            "bsonType": "objectId",
                            "description": "id der Terminart, zB Klausur, Vorbesprechung."
                        },
                        "raum": {
                            "bsonType": "objectId",
                            "description": "_id des Raums des Termins."
                        },
                        "person": {
                            "bsonType": "array",
                            "description": "Die Personen, die an dem Termin teilnehmen.",
                            "items": {
                                "bsonType": "objectId",
                                "description": "Eine Person, die an dem Termin teilnimmt."
                            }
                        },
                        "wochentag": {
                            "enum": ["", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
                            "description": "Der Wochentag."
                        },
                        "start": {
                            "bsonType": ["null", "date"],
                            "description": "Die Zeit, an der der Termin startet."
                        },
                        "ende": {
                            "bsonType": ["null", "date"],
                            "description": "Die Zeit, an der der Termin endet."
                        },
                        "kommentar_de": {
                            "bsonType": "string",
                            "description": "Kommentar zu diesem Termin (de)."
                        },
                        "kommentar_en": {
                            "bsonType": "string",
                            "description": "Kommentar zu diesem Termin (en)."
                        }
                    }
                }
            },
            "einmaliger_termin": {
                "bsonType": "array",
                "description": "Einmalige Termine der Veranstaltung.",
                "items": {
                    "bsonType": "object",
                    "description": "Beschreibung des Termins.",
                    "required": ["key", "raum", "person", "startdatum", "enddatum", "startzeit", "endzeit", "kommentar_de", "kommentar_en"],
                    "properties": {
                        "key": {
                            "bsonType": "objectId",
                            "description": "id der Terminart, zB Klausur, Vorbesprechung."
                        },
                        "raum": {
                            "bsonType": "array",
                            "description": "Räume dieses Termins. (Können zB bei Klausur mehrere sein.)",
                            "items": {
                              "bsonType": "objectId",
                              "description": "_id eines Raumes."
                            }
                        },
                        "person": {
                            "bsonType": "array",
                            "description": "Die Personen, die an dem Termin teilnehmen.",
                            "items": {
                                "bsonType": "objectId",
                                "description": "Eine Person, die an dem Termin teilnimmt."
                            }
                        },
                        "startdatum": {
                            "bsonType": ["null", "date"],
                            "description": "Datum des Termins."
                        },
                        "enddatum": {
                            "bsonType": ["null", "date"],
                            "description": "Datum des Terminendes."
                        },
                        "startzeit": {
                            "bsonType": ["null", "date"],
                            "description": "Uhrzeit des Termins."
                        },
                        "endzeit": {
                            "bsonType": ["null", "date"],
                            "description": "Uhrzeit des Terminendes."
                        },
                         "kommentar_de": {
                            "bsonType": "string",
                            "description": "Kommentar zu diesem Termin (de)."
                        },
                         "kommentar_en": {
                            "bsonType": "string",
                            "description": "Kommentar zu diesem Termin (en)."
                        }
                    }
                }
            },
            "kommentar_html_de": {
                "bsonType": "string",
                "description": "Kommentar (Suffix) für die Homepage."
            },
            "kommentar_html_en": {
                "bsonType": "string",
                "description": "Kommentar (Suffix) für die Homepage."
            },
        }
    }
}

# terminart: Art eines Termins, zB Vorlesung
terminart_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung der Art eines Termins, zB Vorlesung, Vortrag etc",
        "required": ["name_de", "name_en", "hp_sichtbar", "komm_sichtbar", "rang"],
        "properties": {
            "name_de": {
                "bsonType": "string",
                "description": "Die Art eines Termins, Vorlesung, Übung etc -- de"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Die Art eines Termins, Vorlesung, Übung etc -- en"
            },
            "hp_sichtbar": {
                "bsonType": "bool",
                "description": "Zeig an, ob diese Terminart auf der Homepage sichtbar ist"
            },
            "komm_sichtbar": {
                "bsonType": "bool",
                "description": "Zeig an, ob diese Terminart in den Kommentare sichtbar ist"
            },
            "rang": {
                "bsonType": "int",
                "description": "Rang, nach dem (aufsteigend) sortiert wird."
            }
        }
    }
}

