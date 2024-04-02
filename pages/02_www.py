import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import datetime 
import pymongo
import pandas as pd
from itertools import chain

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
from misc.util import *
import misc.tools as tools

# make all neccesary variables available to session_state
setup_session_state()

# Navigation in Sidebar anzeigen
display_navigation()

# Es geht hier vor allem um diese Collection:
collection = veranstaltung
st.session_state.page = "Vorschau"

semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))

if st.session_state.logged_in:
    st.header("Veranstaltungen")
    sem_id = st.selectbox(label="Semester", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester), format_func = (lambda a: semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed")
    st.session_state.semester = sem_id
    if sem_id is not None:
        kat = list(kategorie.find({"semester": sem_id}, sort=[("rang", pymongo.ASCENDING)]))
        st.subheader(f"Lehrveranstaltungen im {semester.find_one({'_id': sem_id})['name_de']}")
        cod = list(code.find({"semester": sem_id, "hp_sichtbar": True}, sort=[("rang", pymongo.ASCENDING)]))
        for c in cod:
            col1, col2 = st.columns([3,27])
            with col1: 
                st.write(c["name"])
            with col2: 
                st.write(c["beschreibung_de"])
        for k in kat:
            st.markdown(k["prefix_de"])
            st.markdown(k["titel_de"])
            st.markdown(k["untertitel_de"])
            # Finde alle Veranstaltungen in der entsprechenden Kategorie
            ver = list(veranstaltung.find({"kategorie": k["_id"], "hp_sichtbar": True},sort=[("rang", pymongo.ASCENDING)]))
            for v in ver:
                col1, col2, col3 = st.columns([3,20,7])
                with col1:
                    code_list = [code.find_one({"hp_sichtbar": True, "_id": c}) for c in v["code"]]
                    st.write(", ".join([c["name"] for c in code_list]))
                with col2:
                    titel_mit_link = f"[{v['name_de']}]({v['url']})" if v['url'] != "" else v['name_de']
                    st.markdown(titel_mit_link)
                    for t in v['woechentlicher_termin']:
                        a = f"{t['key']}"
                        b = wochentag[t["wochentag"]]
                        c = f"{hour_of_datetime(t['start'])}–{hour_of_datetime(t['ende'])}"
                        if c == "–":
                            c = ""
                        r = raum.find_one({"_id": t["raum"]})
                        g = gebaeude.find_one({"_id": r["gebaeude"]})
                        raum_str = f"{r['name_de']} ([{g['name_de']}]({g['url']}))" if g["url"] else g["name_de"]
                        if raum_str == "-":
                            raum_str = ""
                        partline = (", ".join([x for x in [b, c, raum_str] if x != ""]))
                        line = ": ".join([x for x in [a, partline] if x != ""])
                        st.markdown(line)
                with col3:
                    dozenten_liste = [person.find_one({"_id": c}) for c in v["dozent"]]
                    st.markdown(", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in dozenten_liste]))
                col1, col2, col3 = st.columns([3,20,7])

                if v["assistent"] != []:
                    with col2:
                        st.markdown("Assistenz")
                    with col3:
                        assistenten_liste = [person.find_one({"_id": c}) for c in v["assistent"]]
                        st.markdown(", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in assistenten_liste]))
                if v["organisation"] != []:
                    with col2:
                        st.markdown("Organisation")
                    with col3:
                        organisation_liste = [person.find_one({"_id": c}) for c in v["Organsation"]]
                        st.markdown(", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in organisation_liste]))
                    
                st.write(" ")
                st.write(" ")
            st.markdown(k["suffix_de"])

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
