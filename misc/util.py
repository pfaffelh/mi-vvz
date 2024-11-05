import streamlit as st
from misc.config import *
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
        st.session_state.codekategorie = mongo_db["codekategorie"]
        st.session_state.gebaeude = mongo_db["gebaeude"]
        st.session_state.rubrik = mongo_db["rubrik"]
        st.session_state.modul = mongo_db["modul"]
        st.session_state.person = mongo_db["person"]
        st.session_state.raum = mongo_db["raum"]
        st.session_state.semester = mongo_db["semester"]
        st.session_state.studiengang = mongo_db["studiengang"]
        st.session_state.terminart = mongo_db["terminart"]
        st.session_state.veranstaltung = mongo_db["veranstaltung"]
        st.session_state.dictionary = mongo_db["dictionary"]
        st.session_state.planung = mongo_db["planung"]
        st.session_state.planungveranstaltung = mongo_db["planungveranstaltung"]
        
    except: 
        logger.error("Verbindung zur Datenbank nicht möglich!")
        st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

    user = st.session_state.user
    group = st.session_state.group
    anforderung = st.session_state.anforderung
    anforderungkategorie = st.session_state.anforderungkategorie
    code = st.session_state.code
    codekategorie = st.session_state.codekategorie
    gebaeude = st.session_state.gebaeude
    rubrik = st.session_state.rubrik
    modul = st.session_state.modul
    person = st.session_state.person
    raum = st.session_state.raum
    semester = st.session_state.semester
    studiengang = st.session_state.studiengang
    terminart = st.session_state.terminart
    veranstaltung = st.session_state.veranstaltung
    dictionary = st.session_state.dictionary
    planungveranstaltung = st.session_state.planungveranstaltung
    planung = st.session_state.planung
    
    # sem ist ein gewähltes Semester
    if "current_semester_id" not in st.session_state:
        semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.current_semester_id = semesters[0]["_id"]
    if "semester_id" not in st.session_state:
        semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.semester_id = semesters[0]["_id"]
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
    if "de_new" not in st.session_state:
        st.session_state.de_new = ""
    if "en_new" not in st.session_state:
        st.session_state.en_new = ""
    if "kommentar_new" not in st.session_state:
        st.session_state.kommentar_new = ""

    ### temporary data ###
    ### should be also cleared on every page with tools.
    # data for new termine
    if "veranstaltung_tmp" not in st.session_state:
        st.session_state.veranstaltung_tmp = dict()
    # data for translations
    if "translation_tmp" not in st.session_state:
        st.session_state.translation_tmp = None  # Could be specified

    st.session_state.collection_name = {
        anforderung: "Anforderungen",
        anforderungkategorie: "Anforderungskategorien",
        code: "Codes",
        codekategorie: "Codekategorie",
        gebaeude: "Gebäude",
        modul: "Module",
        person: "Personen",
        raum: "Räume",
        rubrik: "Rubrik",
        semester: "Semester",
        studiengang: "Studiengänge",
        terminart: "Terminart",
        veranstaltung: "Veranstaltungen",
        dictionary: "Lexikon",
        planungveranstaltung: "Planungskategorie",
        planung: "Planung"
    }

    st.session_state.leer = {
        anforderung: anforderung.find_one({"name_de": "-"})["_id"],
        anforderungkategorie: anforderungkategorie.find_one({"name_de": "-"})["_id"],
        code: "",
        codekategorie: codekategorie.find_one({"semester": st.session_state.semester_id, "name_de": "-"})["_id"] if len(list(codekategorie.find({"semester": st.session_state.semester_id, "name_de": "-"}))) else "",
        gebaeude: gebaeude.find_one({"name_de": "-"})["_id"],
        modul: modul.find_one({"name_de": "-"})["_id"],
        person: person.find_one({"name": "-"})["_id"],
        raum: raum.find_one({"name_de": "-"})["_id"],
        studiengang: studiengang.find_one({"name": "-"})["_id"],
        rubrik: rubrik.find_one({"semester": st.session_state.semester_id, "titel_de": "-"})["_id"] if len(list(rubrik.find({"semester": st.session_state.semester_id, "titel_de": "-"}))) else "",
        terminart: terminart.find_one({"name_de": "-"})["_id"],
        dictionary: "",
        planungveranstaltung: planungveranstaltung.find_one({"name": "-"})["_id"],
        planung: ""
    }
    leer = st.session_state.leer

    semester_id = st.session_state.semester_id
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
                "name_en": "", 
                "vorname": "", 
                "name_prefix": "", 
                "titel": "", 
                "tel": "", 
                "kommentar": "", 
                "email": "", 
                "url": "", 
                "sichtbar": True, 
                "hp_sichtbar": True, 
                "semester": [st.session_state.semester_id], 
                "veranstaltung": [] 
        },
        studiengang: {"name": "Neuer Studiengang",
                "kurzname": "", 
                "kommentar": "", 
                "sichtbar": True,
                "modul": [],
                "semester": []
        },
        modul: {"name_de": "Neues Modul",
                "name_en": "",
                "kurzname": "", 
                "kommentar": "", 
                "sichtbar": True,
                "studiengang": [] 
        },
        rubrik: {"titel_de": "Neue Rubrik",
                "titel_en": "",
                "untertitel_de": "", 
                "untertitel_en": "", 
                "prefix_de": "", 
                "prefix_en": "", 
                "suffix_de": "", 
                "suffix_en": "", 
                "hp_sichtbar": True,
                "veranstaltung": [] ,
                "kommentar": "",
                "semester": st.session_state.semester_id                
        },
        code:  {"name": "",
                "beschreibung_de": "Neuer Code",
                "beschreibung_en": "", 
                "codekategorie": leer[codekategorie],
                "veranstaltung": [] ,
                "kommentar": "", 
                "semester": st.session_state.semester_id
        },
        codekategorie:  {
                "name_de": "Neu",
                "name_en": "",
                "beschreibung_de": "",
                "beschreibung_en": "", 
                "hp_sichtbar": True,
                "code": [],
                "semester": [],
                "kommentar": "",
                "komm_sichtbar" : False
        },
        terminart: {"name_de": "Neu",
                    "name_en": "",
                    "hp_sichtbar": True,
                    "komm_sichtbar": True,
                    "cal_sichtbar": False
        },
        anforderung: {"name_de": "Neu",
                    "name_en": "",
                    "anforderungskategorie": leer[anforderungkategorie],
                    "kommentar": "", 
                    "sichtbar": True,
                    "semester": [st.session_state.semester_id]
        },
        anforderungkategorie: {
            "name_de": "Neu",
            "name_en": "",
            "kommentar": "", 
            "sichtbar": True,
            "kurzname" : ""
        },
        planungveranstaltung: {
            "name": "",
            "sws": "",
            "regel": "Jedes Wintersemester",
            "kommentar": ""
        },
        planung: {
            "dozent": [],
            "sem": "",
            "kommentar": "",
            "veranstaltung": leer[planungveranstaltung]
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
        raum    : [{"collection": veranstaltung, "field": "einmaliger_termin.$.raum", "list": True}, 
                    {"collection": veranstaltung, "field": "woechentlicher_termin.raum", "list": False}],
        semester: [{"collection": veranstaltung, "field": "semester", "list": False},
                    {"collection": person, "field": "semester", "list": True},
                    {"collection": studiengang, "field": "semester", "list": True},
                    {"collection": rubrik, "field": "semester", "list": False}, 
                    {"collection": code, "field": "semester", "list": False},
                    {"collection": codekategorie, "field": "semester", "list": False}, ],
        rubrik: [{"collection": semester, "field": "rubrik", "list": True}, 
                    {"collection": veranstaltung, "field": "rubrik", "list": False}],
        code:     [{"collection": semester, "field": "code", "list": True}, 
                    {"collection": codekategorie, "field": "code", "list": True},
                    {"collection": veranstaltung, "field": "code", "list": True}],
        codekategorie: [{"collection": code, "field": "codekategorie", "list": False}],
        person  : [{"collection": veranstaltung, "field": "dozent", "list": True}, 
                    {"collection": veranstaltung, "field": "assistent", "list": True}, 
                    {"collection": veranstaltung, "field": "organisation", "list": True}, 
                    {"collection": veranstaltung, "field": "einmaliger_termin.$.person", "list": True}, 
                    {"collection": veranstaltung, "field": "woechentlicher_termin.$.person", "list": True},
                    {"collection": planung, "field": "dozent", "list": True}],
        studiengang:[{"collection": modul, "field": "studiengang", "list": True}],
        modul:     [{"collection": studiengang, "field": "modul", "list": True}, 
                    {"collection": veranstaltung, "field": "verwendbarkeit_modul", "list": True},
                    {"collection": veranstaltung, "field": "verwendbarkeit.modul", "list": False}],
        anforderungkategorie: [{"collection": anforderung, "field": "anforderungskategorie", "list": False}],
        anforderung:[{"collection": veranstaltung, "field": "verwendbarkeit_anforderung", "list": True},
                    {"collection": veranstaltung, "field": "verwendbarkeit.anforderung", "list": False}],
        terminart:[{"collection": veranstaltung, "field": "woechentlicher_termin.key", "list": False},
                    {"collection": veranstaltung, "field": "einmaliger_termin.key", "list": False}],
        veranstaltung:[{"collection": semester, "field": "veranstaltung", "list": True},
                    {"collection": rubrik, "field": "veranstaltung", "list": True},
                    {"collection": code, "field": "veranstaltung", "list": True},
                    {"collection": person, "field": "veranstaltung", "list": True}],
        dictionary: [],
        planung: [],
        planungveranstaltung: [{"collection": planung, "field": "veranstaltung", "list": False}]
    }

    st.session_state.wochentag = {
        "Montag": {"de": "Mo", "en": "Mon"},
        "Dienstag": {"de": "Di", "en": "Tue"},
        "Mittwoch": {"de": "Mi", "en": "Wed"},
        "Donnerstag": {"de": "Do", "en": "Thu"},
        "Freitag": {"de": "Fr", "en": "Fri"},
        "Samstag": {"de": "Sa", "en": "Sat"},
        "Sonntag": {"de": "So", "en": "Sun"},
        "": {"de": "", "en": ""}
    }

setup_session_state()
user = st.session_state.user
group = st.session_state.group
anforderung = st.session_state.anforderung
anforderungkategorie = st.session_state.anforderungkategorie
code = st.session_state.code
codekategorie = st.session_state.codekategorie
gebaeude = st.session_state.gebaeude
rubrik = st.session_state.rubrik
modul = st.session_state.modul
person = st.session_state.person
raum = st.session_state.raum
semester = st.session_state.semester
studiengang = st.session_state.studiengang
terminart = st.session_state.terminart
veranstaltung = st.session_state.veranstaltung
dictionary = st.session_state.dictionary
planungveranstaltung = st.session_state.planungveranstaltung
planung = st.session_state.planung
collection_name = st.session_state.collection_name
leer = st.session_state.leer
new = st.session_state.new
hauptraum_ids = st.session_state.hauptraum_ids
abhaengigkeit = st.session_state.abhaengigkeit
wochentag = st.session_state.wochentag

