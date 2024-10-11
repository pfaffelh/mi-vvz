import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pandas as pd
import time
import pymongo

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

from misc.config import *
import misc.util as util
import misc.tools as tools

tools.delete_temporary()

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.studiengang

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Studiengänge")
    st.write("Mit 😎 markierte Studiengänge sind in Auswahlmenüs sichtbar.")
    st.write(" ")
    co1, co2, co3 = st.columns([1,1,23]) 
    with co3:
        if st.button('**Neuen Studiengang hinzufügen**'):
            st.session_state.edit = "new"
            switch_page("studiengänge edit")

#    y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))
    y = list(collection.find(sort=[("name", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
#        with co1: 
#            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
#        with co2:
#            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:
            abk = f"{x['name'].strip()} ({x['kurzname'].strip()})"
            abk = f"{abk.strip()} 😎" if x["sichtbar"] else f"{abk.strip()}"
            submit = st.button(abk, key=f"edit-{x['_id']}")
        if submit:
            st.session_state.edit = x["_id"]
            switch_page("studiengänge edit")

    with st.expander("Studiengang-Modul-Matrix"):
        st.write("Es werden nur Studiengänge des aktuellen Semesters angezeigt.")
        allstu = util.studiengang.find({"semester" : { "$elemMatch" : { "$eq": st.session_state.semester_id}}}, sort=[("rang", pymongo.ASCENDING)])
        records = [{"studiengang": s["kurzname"], "modul": tools.repr(util.modul, m, False, True)} for s in allstu for m in s["modul"] ]
        df = pd.DataFrame.from_records(records)
        df_crosstab = pd.crosstab(df["modul"], df["studiengang"]) > 0
        df_crosstab = df_crosstab.sort_index(axis=1)
        st.write(df_crosstab)

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)

