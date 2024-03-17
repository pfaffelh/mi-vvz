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
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - MI-FAQ - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = configure_logging(log_file)

def logo():
    add_logo("misc/ufr.png", height=600)

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

def setup_session_state():
    # sem ist ein gewähltes Semester
    if "sem" not in st.session_state:
        st.session_state.sem = None
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
    #st.sidebar.markdown("<img src='./app/static/ufr.png'/>", unsafe_allow_html=True)
    #st.markdown(
    #    '<img src="./app/static/ufr.png" height="333" style="border: 5px solid orange">',
    #    unsafe_allow_html=True,
    #)

    # st.sidebar.image("static/ufr.png")
    st.sidebar.write("<hr style='height:1px;margin:0px;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("VVZ.py", label="VVZ")
    st.sidebar.page_link("pages/01_Veranstaltungen.py", label="Veranstaltungen")
    st.sidebar.page_link("pages/02_Veranstaltungs-Kategorien.py", label="Veranstaltungs-Kategorien")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/03_Personen.py", label="Personen")
    st.sidebar.page_link("pages/04_Gruppen.py", label="Gruppen")
    st.sidebar.page_link("pages/05_Personen-Kategorien.py", label="Personen-Kategorien")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/06_Studiengänge.py", label="Studiengänge")
    st.sidebar.page_link("pages/07_Module.py", label="Module")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/08_Räume.py", label="Räume")
    st.sidebar.page_link("pages/09_Gebäude.py", label="Gebäude")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/10_Semester.py", label="Semester")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/11_Dokumentation.py", label="Dokumentation")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)

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

