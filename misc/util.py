import streamlit as st
from misc.config import *
import ldap
import pymongo

# Initialize logging
import logging
from misc.config import log_file

@st.cache_resource
def configure_logging(file_path, level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - MI-VVZ - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = configure_logging(log_file)

def setup_session_state():
    # Das ist die mongodb; 
    # vvz enthält alle Daten für das Vorlesungsverzeichnis. 
    # user ist aus dem Cluster user und wird nur bei der Authentifizierung benötigt
    try:
        cluster = pymongo.MongoClient(mongo_location)
        mongo_db_users = cluster["user"]
        st.session_state.user = mongo_db_users["user"]
        st.session_state.group = mongo_db_users["group"]

        mongo_db = cluster["vvz"]
        logger.debug("Connected to MongoDB")
        st.session_state.anforderung = mongo_db["anforderung"]
        st.session_state.anforderungkategorie = mongo_db["anforderungkategorie"]
        st.session_state.code = mongo_db["code"]
        st.session_state.gebaeude = mongo_db["gebaeude"]
        st.session_state.kategorie = mongo_db["kategorie"]
        st.session_state.modul = mongo_db["modul"]
        st.session_state.person = mongo_db["person"]
        st.session_state.raum = mongo_db["raum"]
        st.session_state.semester = mongo_db["semester"]
        st.session_state.studiengang = mongo_db["studiengang"]
        st.session_state.veranstaltung = mongo_db["veranstaltung"]

    except: 
        logger.error("Verbindung zur Datenbank nicht möglich!")
        st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

    user = st.session_state.user
    group = st.session_state.group
    anforderung = st.session_state.anforderung
    anforderungkategorie = st.session_state.anforderungkategorie
    code = st.session_state.code
    gebaeude = st.session_state.gebaeude
    kategorie = st.session_state.kategorie
    modul = st.session_state.modul
    person = st.session_state.person
    raum = st.session_state.raum
    semester = st.session_state.semester
    studiengang = st.session_state.studiengang
    veranstaltung = st.session_state.veranstaltung


    # sem ist ein gewähltes Semester
    if "current_semester_id" not in st.session_state:
        semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.current_semester_id = semesters[0]["_id"]
    # expanded zeigt an, welches Element ausgeklappt sein soll
    if "expanded" not in st.session_state:
        st.session_state.expanded = ""
    # Name of the user
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    # Element to edit
    if "edit" not in st.session_state:
        st.session_state.edit = ""
    # Determines which page we are on
    if "page" not in st.session_state:
        st.session_state.page = ""

    st.session_state.collection_name = {
        gebaeude: "Gebäude",
        raum: "Räume",
        semester: "Semester",
        kategorie: "Kategorien",
        code: "Codes",
        person: "Personen",
        studiengang: "Studiengänge",
        modul: "Module",
        anforderung: "Anforderungen",
        anforderungkategorie: "Anforderungskategorien",
        veranstaltung: "Veranstaltungen"
    }

    st.session_state.leer = {
        gebaeude: gebaeude.find_one({"name_de": "-"})["_id"],
        raum: raum.find_one({"name_de": "-"})["_id"],
        person: person.find_one({"name": "-"})["_id"],
        studiengang: studiengang.find_one({"name": "-"})["_id"],
        modul: modul.find_one({"name_de": "-"})["_id"],
        kategorie: "",
        anforderung: "",
        code: "",    
        anforderungkategorie: anforderungkategorie.find_one({"name_de": "-"})["_id"]
    }
    leer = st.session_state.leer

    semester_id = semester.find_one()["_id"]
    st.session_state.new = {
        gebaeude: {"name_de": "neu", 
                "name_en": "", 
                "kurzname": "", 
                "adresse": "", 
                "url": "", 
                "sichtbar": True, 
                "kommentar": ""},
        raum: {"name_de": "neu", 
            "name_en": "", 
            "kurzname": "", 
            "gebaeude": leer[gebaeude], 
            "raum": "", 
            "groesse": 0, 
            "sichtbar": True, 
            "kommentar": ""
        },
        person: {"name": "Neue Person",
                "vorname": "", 
                "name_prefix": "", 
                "titel": "", 
                "tel": "", 
                "email": "", 
                "sichtbar": True, 
                "hp_sichtbar": True, 
                "semester": [], 
                "veranstaltung": [] 
        },
        studiengang: {"name": "Neuer Studiengang",
                "kurzname": "", 
                "kommentar": "", 
                "sichtbar": True,
                "modul": [] 
        },
        modul: {"name_de": "Neues Modul",
                "name_en": "Neues Modul",
                "kurzname": "", 
                "kommentar": "", 
                "sichtbar": True,
                "studiengang": [] 
        },
        kategorie: {"titel_de": "Neue Kategorie",
                "titel_en": "",
                "untertitel_de": "", 
                "untertitel_en": "", 
                "prefix_de": "", 
                "prefix_en": "", 
                "suffix_de": "", 
                "suffix_en": "", 
                "hp_sichtbar": True,
                "veranstaltung": [] ,
                "kommentar": ""
        },
        code:  {"name": "",
                "beschreibung_de": "Neuer Code",
                "beschreibung_en": "", 
                "hp_sichtbar": True,
                "veranstaltung": [] ,
                "kommentar": "", 
                "semester": semester_id
        },
        anforderung: {"name_de": "Neu",
                    "name_en": "",
                    "anforderungskategorie": leer[anforderungkategorie],
                    "kommentar": "", 
                    "sichtbar": True
        },
        anforderungkategorie: {
            "name_de": "Neu",
            "name_en": "",
            "kommentar": "", 
            "sichtbar": True
        }
    }
    # Für den Raumplan
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
    st.session_state.hauptraum_ids = [r["_id"] for r in hauptraum]


    st.session_state.abhaengigkeit = {
        gebaeude: [{"collection": raum, "field": "gebaeude", "list": False}],
        raum    : [{"collection": veranstaltung, "field": "einmaliger_termin.raum", "list": False}, 
                    {"collection": veranstaltung, "field": "woechentlicher_termin.raum", "list": False}],
        semester: [{"collection": veranstaltung, "field": "semester", "list": False},
                    {"collection": person, "field": "semester", "list": True},
                    {"collection": kategorie, "field": "semester", "list": False}, 
                    {"collection": code, "field": "semester", "list": False}, ],
        kategorie:[{"collection": semester, "field": "kategorie", "list": True}, 
                    {"collection": veranstaltung, "field": "kategorie", "list": False}],
        code:     [{"collection": semester, "field": "code", "list": True}, 
                    {"collection": veranstaltung, "field": "code", "list": True}],
        person  : [{"collection": veranstaltung, "field": "dozent", "list": True}, 
                    {"collection": veranstaltung, "field": "assistent", "list": True}, 
                    {"collection": veranstaltung, "field": "organisation", "list": True}, 
                    {"collection": veranstaltung, "field": "einmaliger_termin.person", "list": False}, 
                    {"collection": veranstaltung, "field": "woechentlicher_termin.person", "list": False}],
        studiengang:[{"collection": modul, "field": "studiengang", "list": True}],  
        modul:     [{"collection": studiengang, "field": "modul", "list": True}, 
                    {"collection": veranstaltung, "field": "verwendbarkeit_modul", "list": True},
                    {"collection": veranstaltung, "field": "verwendbarkeit.modul", "list": False}],
        anforderungkategorie: [{"collection": anforderung, "field": "anforderungskategorie", "list": False}],
        anforderung:[{"collection": veranstaltung, "field": "verwendbarkeit_anforderung", "list": True},
                    {"collection": veranstaltung, "field": "verwendbarkeit.anforderung", "list": False}],
        veranstaltung:[{"collection": semester, "field": "veranstaltung", "list": True},
                    {"collection": kategorie, "field": "veranstaltung", "list": True},
                    {"collection": code, "field": "veranstaltung", "list": True},
                    {"collection": person, "field": "veranstaltung", "list": True}]
    }

    st.session_state.wochentag = {
        "Montag": "Mo",
        "Dienstag": "Di",
        "Mittwoch": "Mi",
        "Donnerstag": "Do",
        "Freitag": "Fr",
        "Samstag": "Sa",
        "Sonntag": "So",
        None: ""
    }

setup_session_state()
user = st.session_state.user
group = st.session_state.group
anforderung = st.session_state.anforderung
anforderungkategorie = st.session_state.anforderungkategorie
code = st.session_state.code
gebaeude = st.session_state.gebaeude
kategorie = st.session_state.kategorie
modul = st.session_state.modul
person = st.session_state.person
raum = st.session_state.raum
semester = st.session_state.semester
studiengang = st.session_state.studiengang
veranstaltung = st.session_state.veranstaltung
collection_name = st.session_state.collection_name
leer = st.session_state.leer
new = st.session_state.new
hauptraum_ids = st.session_state.hauptraum_ids
abhaengigkeit = st.session_state.abhaengigkeit
wochentag = st.session_state.wochentag

