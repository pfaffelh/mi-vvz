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

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.terminart

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Art eines Termins")
    st.write("Mit 😎 markierte Terminarten, die auf der Homepage sichtbar sind.")
    st.write("Mit 🤓 markierte Terminarten, die im kommentierten VVZ sichtbar sind.")
    st.write(" ")
    co1, co2, co3 = st.columns([1,1,23]) 
    with co3:
        if st.button('**Neue Terminart hinzufügen**'):
            st.session_state.edit = "new"
            switch_page("terminart edit")

    y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:
            abk = f"{x['name_de'].strip()}"
            abk = f"{abk.strip()} 😎" if x["hp_sichtbar"] else f"{abk.strip()}"
            abk = f"{abk.strip()} 🤓" if x["komm_sichtbar"] else f"{abk.strip()}"
            submit = st.button(abk, key=f"edit-{x['_id']}")
        if submit:
            st.session_state.edit = x["_id"]
            switch_page("terminart edit")


else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)



