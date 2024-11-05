import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, timedelta
import pymongo
import pandas as pd

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

from misc.config import *
import misc.util as util
import misc.tools as tools

tools.delete_temporary()

# Navigation in Sidebar anzeigen
tools.display_navigation()
st.session_state.page = "Suchen"

if st.session_state.logged_in:
    st.header("Suche nach Veranstaltungen / Terminen")
    with st.expander("Suche nach Veranstaltungen..."):
        st.write("...auf die folgendes zutrifft:")
        st.write("(Die einzelnen Zeilen sind mit 'und' verknüpft. Die eingegebenen Wörter im Textfeld sind mit 'oder' verknüpft.)")
        # QUERY
        # Auswahl von Semester
        semesters = list(util.semester.find(sort=[("rang", pymongo.DESCENDING)]))
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write("von...")
            semester_id_von = st.selectbox(label="von", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_von")
            semester_von = util.semester.find_one({"_id": semester_id_von})
        with col2:
            st.write("...bis...")
            semester_id_bis = st.selectbox(label="bis", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_bis")
            semester_bis = util.semester.find_one({"_id": semester_id_bis})
        semester_auswahl = list(util.semester.find({"rang": {"$gte": semester_von["rang"], "$lte": semester_bis["rang"]}}))

        # Auswahl von Rubriken 
        rubrik_vorauswahl = list(util.rubrik.find({"semester": {"$in": [x["_id"] for x in semester_auswahl]}, "veranstaltung": {"$ne": []}}, sort = [("titel_de", pymongo.ASCENDING)]))
        rubrik_list = st.multiselect("Rubriken", [x["_id"] for x in rubrik_vorauswahl], [], format_func = (lambda a: tools.repr(util.rubrik, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchte Veranstaltung muss einen der ausgewählten Rubriken tragen. Falls keine Rubrik angegeben ist, werden Rubriken in der Suche nicht berücksichtigt.")

        # Auswahl von Codes
        code_vorauswahl = list(util.code.find({"semester": {"$in": [x["_id"] for x in semester_auswahl]}, "veranstaltung": {"$ne": []}}, sort = [("beschreibung_de", pymongo.ASCENDING)]))
        code_list = st.multiselect("Codes", [x["_id"] for x in code_vorauswahl], [], format_func = (lambda a: tools.repr(util.code, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchten Veranstaltungen müssen einen der ausgewählten Codes tragen. Falls kein Code angegeben ist, werden Codes in der Suche nicht berücksichtigt.")

        # Auswahl von Personen
        person_vorauswahl = list(util.person.find({"semester": {"$elemMatch": {"$in": [x["_id"] for x in semester_auswahl]}}, "veranstaltung": {"$ne": []}}, sort = [("name", pymongo.ASCENDING)]))
        person_list = st.multiselect("Personen", [x["_id"] for x in person_vorauswahl], [], format_func = (lambda a: tools.repr(util.person, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchten Veranstaltungen müssen mit einer der ausgewählten Personen verbunden sein. Falls kein Code angegeben ist, werden Codes in der Suche nicht berücksichtigt.")

        # Freitextsuche im Titel
        te = st.text_input("Titel enthält", help = "Es wird nach ganzen Wörtern mit einer oder-Verknüpfung gesucht")

        # Erstellung der Query
        query = {}
        query["semester"] = {"$in": [x["_id"] for x in semester_auswahl]}
        if code_list:
            query["code"] = {"$elemMatch": { "$in": code_list}}
        if rubrik_list:
            query["rubrik"] = {"$in": rubrik_list}
        if person_list:
            query["$or"] = [{"dozent": {"$elemMatch": { "$in": person_list}}}, {"assistent": {"$elemMatch": { "$in": person_list}}}, {"organisation": {"$elemMatch": { "$in": person_list}}}]
        if te:
            query["$text"] = {"$search": f'{te}'}

        result = list(util.veranstaltung.find(query))

        st.divider()
        st.write("### Folgende Felder werden ausgegeben")
        # Auswahl der Ausgabe
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
        with col1:
            ausgabe_semester = st.checkbox("Semester", True)
        with col2:
            ausgabe_rubrik = st.checkbox("Rubrik", True)
        with col3:
            ausgabe_titel = st.checkbox("Titel der Veranstaltung", True)
        with col4:
            ausgabe_dozent = st.checkbox("Dozent*innen", True)
        with col5:
            ausgabe_assistent = st.checkbox("Assistent*innen", True)

        semester = [tools.repr(util.semester, r["semester"], False, True) for r in result]
        titel = [r["name_de"] for r in result]
        rubrik = [tools.repr(util.rubrik, r["rubrik"], False, True) for r in result]
        titel = [r["name_de"] for r in result]
        dozent = [", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in [util.person.find_one({"_id": p}) for p in r["dozent"]]]) for r in result]
        assistent = [", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in [util.person.find_one({"_id": p}) for p in r["assistent"]]]) for r in result]

        dict = {}
        if ausgabe_semester:
            dict["Semester"] = semester
        if ausgabe_rubrik:
            dict["Rubrik"] = rubrik
        if ausgabe_titel:
            dict["Veranstaltung"] = titel    
        if ausgabe_dozent:
            dict["Dozent*innen"] = dozent
        if ausgabe_assistent:
            dict["Assistent*innen"] = assistent

        df = pd.DataFrame(dict)

        st.divider()

        st.data_editor(df, use_container_width=True, hide_index=True)   

    with st.expander("Suche nach einmaligen Terminen..."):
        st.write("")
        anzeige_start = st.date_input("von", value = datetime.now() + timedelta(days = -30),  label_visibility="hidden", placeholder = "von")
        st.write("...und...")
        anzeige_ende = st.date_input("bis", value = datetime.now() + timedelta(days = 90), label_visibility="hidden", placeholder = "bis")

        nur_cal = st.toggle("Genau die Termine aus dem Prüfungskalender")
        ter_list = [ta["_id"] for ta in list(util.terminart.find({"cal_sichtbar" : True}))]
        ta_list = st.multiselect("Terminarten", [x["_id"] for x in rubrik_vorauswahl], ter_list if nur_cal else [], format_func = (lambda a: tools.repr(util.terminart, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchte Veranstaltung muss einen der ausgewählten Rubriken tragen. Falls keine Rubrik angegeben ist, werden Rubriken in der Suche nicht berücksichtigt.")
        



else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
