import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import datetime 
import pymongo
import pandas as pd
from itertools import chain
from bson import ObjectId

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
import misc.util as util
import misc.tools as tools

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.veranstaltung

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("Veranstaltungen")
    # semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
    # st.session_state.semester_id = st.selectbox(label="Semester", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.current_semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed")
    if st.session_state.semester_id is not None:
        kat = list(util.rubrik.find({"semester": st.session_state.semester_id}, sort=[("rang", pymongo.ASCENDING)]))
        for k in kat:
            st.write(k["titel_de"])
            ver = list(util.veranstaltung.find({"rubrik": k["_id"]},sort=[("rang", pymongo.ASCENDING)]))
            for v in ver:
                col1, col2, col3 = st.columns([1,1,23]) 
                with col1:
                    st.button('↓', key=f'down-{v["_id"]}', on_click = tools.move_down, args = (collection, v,{"rubrik": v["rubrik"]}, ))
                with col2:
                    st.button('↑', key=f'up-{v["_id"]}', on_click = tools.move_up, args = (collection, v, {"rubrik": v["rubrik"]},))
                with col3:
                    d = [(util.person.find_one({"_id": x}))["name"] for x in v["dozent"]]
                    s = f"{v['name_de']} ({', '.join(d) if d else ''})"
                    submit = st.button(s, key=f"edit-{v['_id']}")
                if submit:
                    st.session_state.edit = v["_id"]
                    st.session_state.expanded = "termine"
                    switch_page("veranstaltungen edit")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
