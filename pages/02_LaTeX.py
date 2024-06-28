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

    sem_id = st.session_state.semester_id
    sem_kurzname = util.semester.find_one({"_id" : sem_id})["kurzname"]
    data = latex.makedata(sem_kurzname)

    wasserzeichen = "Test"
    template = latex.latex_jinja_env.get_template(f"static/template.tex")
    document = template.render(data = data)

    st.download_button("Download kommentiertes VVZ", document, file_name=f"Kommentare_{sem_kurzname}.tex", help=None, on_click=None, args=None, kwargs=None)


