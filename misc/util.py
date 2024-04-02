import streamlit as st
from misc.config import *
import ldap
from streamlit_extras.app_logo import add_logo
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

def logo():
    add_logo("static/ufr.png", height=600)

def login():
    st.session_state.logged_in = True
    st.success("Login erfolgreich.")
    logger.info(f"User {st.session_state.user} hat sich eingeloggt.")

def logout():
    st.session_state.logged_in = False
    logger.info(f"User {st.session_state.user} hat sich ausgeloggt.")

# Sprache zwischen Deutsch und Englisch hin- und herwechseln
def change_lang():
    st.session_state.lang = ("de" if st.session_state.lang == "en" else "en")

# Wechseln zwischen Aus- und Einklappen aller Fragen
def change_expand_all():
    st.session_state.expand_all = (False if st.session_state.expand_all == True else True)

# Das ist die mongodb; 
# vvz enthält alle Daten für das Vorlesungsverzeichnis. 
# user ist aus dem Cluster user und wird nur bei der Authentifizierung benötigt
try:
    cluster = pymongo.MongoClient(mongo_location)
    mongo_db = cluster["vvz"]
    anforderung = mongo_db["anforderung"]
    anforderungkategorie = mongo_db["anforderungkategorie"]
    code = mongo_db["code"]
    gebaeude = mongo_db["gebaeude"]
    kategorie = mongo_db["kategorie"]
    modul = mongo_db["modul"]
    person = mongo_db["person"]
    raum = mongo_db["raum"]
    semester = mongo_db["semester"]
    studiengang = mongo_db["studiengang"]
    veranstaltung = mongo_db["veranstaltung"]

    mongo_db_users = cluster["user"]
    user = mongo_db_users["user"]
except: 
    logger.error("Verbindung zur Datenbank nicht möglich!")
    st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

collection_name = {
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

def setup_session_state():
    # sem ist ein gewähltes Semester
    if "semester" not in st.session_state:
        semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.semester = semesters[0]["_id"]
    # lang ist die Sprache (de, en)
    if "lang" not in st.session_state:
        st.session_state.lang = "de"
    # submitted wird benötigt, um nachzufragen ob etwas wirklich gelöscht werden soll
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    # st.session_state.expand_all bestimmt, ob all QA-Paare aufgeklappt dargestellt werden oder nicht
    if "expand_all" not in st.session_state:
        st.session_state.expand_all = False
    # expanded zeigt an, welches Element ausgeklappt sein soll
    if "expanded" not in st.session_state:
        st.session_state.expanded = ""
    # category gibt an, welche category angezeigt wird
    if "category" not in st.session_state:
        st.session_state.category = None
    # Name of the user
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
    # Element to update
    if "update" not in st.session_state:
        st.session_state.update = False
    if "new" not in st.session_state:
        st.session_state.new = False
    # Element to delete
    if "delete" not in st.session_state:
        st.session_state.delete = False
    # Element to delete
    if "edit" not in st.session_state:
        st.session_state.edit = ""
    # Determines which page we are on
    if "page" not in st.session_state:
        st.session_state.page = ""

setup_session_state()

# Diese Funktion löschen, wenn die Verbindung sicher ist.
def authenticate2(username, password):
    return True if password == "0761" else False

# Die Authentifizierung gegen den Uni-LDAP-Server
def authenticate(username, password):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    user_dn = "uid={},{}".format(username, base_dn)
    try:
        l = ldap.initialize(server)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.LDAPError as error:
        logger.warning(f"LDAP-Error: {error}")
        return False

def can_edit(username):
    u = user.find_one({"rz": username})
    faq_id = group.find_one({"name": "faq"})["_id"]
    return (True if faq_id in u["groups"] else False)

# Das ist die mongodb; 
# QA-Paar ist ein Frage-Antwort-Paar aus dem FAQ.
# category enthält alle Kategorien von QA-Paaren. "invisible" muss es geben!
# qa enthält alle Frage-Antwort-Paare.
# user ist aus dem Cluster users und wird nur bei der Authentifizierung benötigt
try:
    cluster = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mongo_db = cluster["vvz"]
    mongo_db_users = cluster["user"]
    category = mongo_db["category"]
    qa = mongo_db["qa"]
    user = mongo_db_users["user"]
    group = mongo_db_users["group"]
    logger.debug("Connected to MongoDB")
    logger.debug("Database contains collections: ")
    logger.debug(str(mongo_db.list_collection_names()))
except: 
    logger.error("Verbindung zur Datenbank nicht möglich!")
    st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

def reset(text=""):
    st.session_state.submitted = False
    st.session_state.expand_all = False
    st.session_state.expanded = ""
    st.session_state.edit = ""
    if text != "":
        st.success(text)

def authenticate(username, password):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    user_dn = "uid={},{}".format(username, base_dn)
    try:
        l = ldap.initialize(server)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.LDAPError as error:
        print("Error:", error)
        return False

def can_edit(username):
    u = user.find_one({"rz": username})
    print("User is ", username)
    return (True if "faq" in u["groups"] else False)

def display_navigation():
    st.markdown("<style>.st-emotion-cache-16txtl3 { padding: 2rem 2rem; }</style>", unsafe_allow_html=True)
    with st.sidebar:
        col1, col2, col3 = st.columns([1,8,1])
        with col2:
            st.image("static/ufr.png", use_column_width=False)
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("VVZ.py", label="Veranstaltungen")
    st.sidebar.page_link("pages/01_Raumplan.py", label="Raumplan")
    st.sidebar.page_link("pages/02_www.py", label="Vorschau www.math...")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/03_Personen.py", label="Personen")
    st.sidebar.page_link("pages/05_Studiengänge.py", label="Studiengänge")
    st.sidebar.page_link("pages/06_Module.py", label="Module")
    st.sidebar.page_link("pages/07_Anforderungen.py", label="Anforderungen")
    st.sidebar.page_link("pages/08_Räume.py", label="Räume")
    st.sidebar.page_link("pages/09_Gebäude.py", label="Gebäude")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/10_Semester.py", label="Semester")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/11_Dokumentation.py", label="Dokumentation")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)


leer = {
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

semester_id = semester.find_one()["_id"]
new = {
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

def repr(collection, id, show_collection = True):
    x = collection.find_one({"_id": id})
    if collection == gebaeude:
        res = x['name_de']
        if show_collection:
            res = "Gebäude: " + res
    elif collection == raum:
        res = x['name_de']
        if show_collection:
            res = "Raum: " + res
    elif collection == semester:
        res = x['kurzname']
        if show_collection:
            res = "Semester: " + res
    elif collection == kategorie:
        sem = semester.find_one({"_id": x["semester"]})["kurzname"]
        res = f"{x['titel_de']} ({sem})"
        if show_collection:
            res = "Kategorie: " + res
    elif collection == code:
        sem = semester.find_one({"_id": x["semester"]})["kurzname"]
        res = f"{x['beschreibung_de']} ({sem})"    
        if show_collection:
            res = "Code: " + res
    elif collection == person:
        res = f"{x['name']}, {x['name_prefix']}"
        if show_collection:
            res = "Person: " + res
    elif collection == studiengang:
        res = f"{x['name']}"
        if show_collection:
            res = "Studiengang: " + res
    elif collection == modul:
        s = ", ".join([studiengang.find_one({"_id" : id1})["kurzname"] for id1 in x["studiengang"]])
        res = f"{x['name_de']} ({s})"
        if show_collection:
            res = "Modul: " + res
    elif collection == anforderung:
        res = x['name_de']
        if show_collection:
            res = "Anforderung: " + res
    elif collection == anforderungkategorie:
        res = x['name_de']
        if show_collection:
            res = "Anforderungskategorie: " + res
    elif collection == veranstaltung:
        s = ", ".join([person.find_one({"_id" : id1})["name"] for id1 in x["dozent"]])
        sem = semester.find_one({"_id": x["semester"]})["kurzname"]
        res = f"{x['name_de']} ({s}, {sem})"
        if show_collection:
            res = "Veranstaltung: " + res
    return res

abhaengigkeit = {
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

wochentag = {
    "Montag": "Mo",
    "Dienstag": "Di",
    "Mittwoch": "Mi",
    "Donnerstag": "Do",
    "Freitag": "Fr",
    "Samstag": "Sa",
    "Sonntag": "So",
    None: ""
}

def hour_of_datetime(dt):
    if dt is None:
        return ""
    else:
        return str(dt.hour)

def name_of_sem_id(semester_id):
    x = semester.find_one({"_id": semester_id})
    return x["name_de"]

def name_of_ver_id(ver_id):
    x = veranstaltung.find_one({"_id": ver_id})
    return x["name_de"]

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
#hauptraum = [rund, weis, hs2, sr404, sr125, sr127, sr226, sr119, sr218, sr232, sr318, sr403, sr414]
hauptraum = [rund, weis, hs2, sr404, sr125, sr127, sr226]

hauptraum_ids = [r["_id"] for r in hauptraum]

kurzkurzname = {"HsRundbau": "HsR",
                "HsWeismann": "HsW",
                "HSII": "Hs2",
                "SR404": "404",
                "SR125": "125",
                "SR127": "127",
                "SR226": "226",
                "SR119": "119",
                "SR218": "218",
                "R232": "232",
                "SR318": "318",
                "SR403": "403",
                "SR414": "414"
}