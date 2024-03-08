from pymongo import MongoClient

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

# collections sind:

# category
# qa_pair

# Here are the details

# category: Beschreibung einer Kategorie von Fragen
category_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Kategorie von Fragen (zB Abschlussarbeiten).",
        "required": ["kurzname", "name_de", "rang"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Kategorie -- required"
            },
            "name_de": {
                "bsonType": "string",
                "description": "Deutscher Name der Kategorie -- required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Englischer Name der Kategorie -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Ein Kommentar (erscheint nicht auf der Homepage)"
            },
            "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
        }
    }
}

# qa: Ein Paar auf Frage und Antwort
qa_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Frage-Antwort-Paar für das FAQ.",
        "required": ["q-de", "a-de", "category", "rang"],
        "properties": {
            "category": {
                "bsonType": "string",
                "description": "Der Kurzname der Kategorie -- required"
            },
            "q-de": {
                "bsonType": "string",
                "description": "Die Frage (in deutsch) -- required"
            },
            "q-en": {
                "bsonType": "string",
                "description": "Die Frage (in englisch)"
            },
            "a-de": {
                "bsonType": "string",
                "description": "Die Antwort (als markdown, in deutsch) -- required"
            },
            "a-_en": {
                "bsonType": "string",
                "description": "Die Antwort (als markdown, in englisch)"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Ein Kommentar (erscheint nicht auf der Homepage)"
            },
            "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
        }
    }
}

