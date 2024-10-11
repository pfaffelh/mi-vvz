import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
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
collection = util.person

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Personen")
    st.write(" ")

    if st.button('**Neue Person hinzufügen**'):
        st.session_state.edit = "new"
        switch_page("personen edit")

    y = list(collection.find({"semester": { "$elemMatch": {"$eq": st.session_state.semester_id}}}, sort=[("name", pymongo.ASCENDING), ("vorname", pymongo.ASCENDING)]))
    for x in y:
        abk = f"{x['name'].strip()}, {x['vorname'].strip()}".strip()
        submit = st.button(abk, key=f"edit-{x['_id']}")
        if submit:
            st.session_state.edit = x["_id"]
            switch_page("personen edit")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
