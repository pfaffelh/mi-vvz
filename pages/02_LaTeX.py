import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pymongo
import time
import ldap
import misc.util as util
import misc.latex as latex
from bson import ObjectId
from misc.config import *
import pandas as pd
import json, jinja2

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
st.session_state.page = "LaTeX"

if st.session_state.logged_in:
    st.header("Ausgabe von LaTeX-Files")
    st.write("Hier können LaTeX-Files für das kommentierte Vorlesungsverzeichnis und die Erweiterungen der Modulhandbücher ausgegeben werden.")
    st.header("Kommentiertes Vorlesungsverzeichnis")
    st.write("Es werden nur Veranstaltungen aufgenommen, die den Code 'Komm' tragen.")

    sem_id = st.session_state.semester_id
    komm_id = util.code.find_one({"semester" : sem_id, "name" : { "$eq" : "Komm" }})["_id"]
    ver_komm = list(util.veranstaltung.find({"semester" : sem_id, "code" : { "$elemMatch" : { "$eq" : komm_id }}}))
    ver_text = list(util.veranstaltung.find({"semester" : sem_id, "$or" : [{ "inhalt_de" : { "$ne" : ""}}, {"inhalt_en" : { "$ne" : ""}}]}))

    # Veranstaltungen, die den Code Komm haben, aber für die kein Kommentar vorhanden ist
    Delta1 = [tools.repr(util.veranstaltung, v["_id"], False) for v in ver_komm if v not in ver_text]
    # Veranstaltungen, für die ein Kommentar vorhanden ist, die aber den Code Komm nicht tragen
    Delta2 = [tools.repr(util.veranstaltung, v["_id"], False) for v in ver_text if v not in ver_komm]

    if Delta1 != []:
        st.write("#### Veranstaltungen mit Code _Komm_, aber für die kein Kommentar vorhanden ist")
        for v in Delta1:
            st.write(v)
    else:
        st.write("#### Alle Veranstaltungen mit Code _Komm_ verfügen über einen Kommentar.")

    if Delta2 != []:
        st.write("#### Veranstaltungen mit Kommentar, die den Code _Komm_ nicht besitzen")
        for v in Delta2:
            st.write(v)
    else:
        st.write("#### Alle Veranstaltungen mit Kommentar haben Code _Komm_.")

    wasserzeichen = st.text_input('Wasserzeichen, z.B. Vorläufige Version', "")

    sem_id = st.session_state.semester_id
    sem_kurzname = util.semester.find_one({"_id" : sem_id})["kurzname"]
    sem_name = util.semester.find_one({"_id" : sem_id})["name_de"]
    data = latex.makedata(sem_kurzname, komm_id)
    data["wasserzeichen"] = wasserzeichen
    data["semester"] = sem_name

    template = latex.latex_jinja_env.get_template(f"static/template.tex")
    kommentare = template.render(data = data, include_inhalt = True, include_verwendbarkeit = False)

    st.download_button("Download kommentiertes VVZ", kommentare, file_name=f"Kommentare_{sem_kurzname}.tex", help=None, on_click=None, args=None, kwargs=None)


