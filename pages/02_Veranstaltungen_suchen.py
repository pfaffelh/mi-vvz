import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import datetime 
import pymongo
import pandas as pd
from itertools import chain

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

from misc.config import *
import misc.util as util
import misc.tools as tools

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.veranstaltung
st.session_state.page = "Suchen"

if st.session_state.logged_in:
    st.header("Suche nach Veranstaltungen")
    st.write("...auf die folgendes zutrifft:")
    # QUERY
    # Auswahl von Semester
    semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.write("von...")
        semester_id_von = st.selectbox(label="von", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_von")
        semester_von = util.semester.find_one({"_id": semester_id_von})
    with col2:
        st.write("...bis...")
        semester_id_bis = st.selectbox(label="bis", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_bis")
        semester_bis = util.semester.find_one({"_id": semester_id_bis})

    rubrik_list = st.multiselect("Rubriken", [x["_id"] for x in util.rubrik.find({"semester": {"$in": [x["_id"] for x in semesters]}}, sort = [("titel_de", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.rubrik, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchte Veranstaltung muss einen der ausgewählten Rubriken tragen. Falls keine Rubrik angegeben ist, werden Rubriken in der Suche nicht berücksichtigt.")
    # Sortiere codes nach ihrem Rang 
    ru = list(util.rubrik.find({"_id": {"$in": rubrik_list}}, sort=[("rang", pymongo.ASCENDING)]))
    rubrik_list = [r["_id"] for r in ru]

    code_list = st.multiselect("Codes", [x["_id"] for x in util.code.find({}, sort = [("beschreibung_de", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.code, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchte Veranstaltung muss einen der ausgewählten Codes tragen. Falls kein Code angegeben ist, werden Codes in der Suche nicht berücksichtigt.")
    # Sortiere codes nach ihrem Rang 
    co = list(util.code.find({"_id": {"$in": code_list}}, sort=[("rang", pymongo.ASCENDING)]))
    code_list = [c["_id"] for c in co]

    te = st.text_input("Titel (de) enthält")

#    Personen

    semester_auswahl = list(util.semester.find({"kurzname": {"$gte": semester_von["kurzname"], "$lte": semester_bis["kurzname"]}}))

    query = {}
    query["semester"] = {"$in": [x["_id"] for x in semester_auswahl]}
    if code_list:
        query["code"] = {"$elemMatch": { "$in": code_list}}
    if rubrik_list:
        query["rubrik"] = {"$in": code_list}

    result = list(util.veranstaltung.find(query))

    st.divider()
    st.write("### Folgende Felder werden ausgegeben")
    # Auswahl der Ausgabe
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    with col1:
        ausgabe_semester = st.checkbox("Semester", True)
    with col2:
        ausgabe_titel = st.checkbox("Titel der Veranstaltung", True)
    with col3:
        ausgabe_dozent = st.checkbox("Dozent*innen", True)
    with col4:
        ausgabe_assistent = st.checkbox("Assistent*innen", True)



    semester = [tools.repr(util.semester, r["semester"], False, True) for r in result]
    titel = [r["name_de"] for r in result]
    dozent = [", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in [util.person.find_one({"_id": p}) for p in r["dozent"]]]) for r in result]
    assistent = [", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in [util.person.find_one({"_id": p}) for p in r["assistent"]]]) for r in result]

    dict = {}
    if ausgabe_semester:
        dict["Semester"] = semester
    if ausgabe_titel:
        dict["Veranstaltung"] = titel    
    if ausgabe_assistent:
        dict["Assistent*innen"] = assistent
    if ausgabe_dozent:
        dict["Dozent*innen"] = dozent

    df = pd.DataFrame(dict)

    st.divider()

    st.data_editor(df, use_container_width=True, hide_index=True)   

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
