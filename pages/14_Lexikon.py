import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
from pymongo.collation import Collation

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

from misc.config import *
import misc.util as util
from misc.util import logger
import misc.tools as tools

# load css styles
from misc.css_styles import init_css
init_css()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.dictionary

def saveneu(ini):
    collection.insert_one(ini)
    st.toast("Erfolgreich gespeichert!")
    st.session_state.de_new = ""
    st.session_state.en_new = ""
    st.session_state.kommentar_new = ""

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Lexikon (de / en) wichtiger Fachbegriffe")
    # sort case-insensitive
    words = list(collection.find({}, collation = Collation(locale = 'en'), sort=[("de", pymongo.ASCENDING)]))
    st.write("### Neuer Eintrag")
    col = st.columns([2,5,5,5,2])
    with col[1]:
        neu_de = st.text_input('Deutscher Begriff', "", key = "de_new")
    with col[2]:
        neu_en = st.text_input('Englischer Begriff', "", key = "en_new")
    with col[3]:
        neu_kommentar = st.text_input('Kommentar', '', key = "kommentar_new")
    with col[0]:
        st.write("")
        st.write("")
        st.button("Speichern", use_container_width=True, key = f"save_neu", on_click=saveneu, args = [{"de": neu_de, "en": neu_en, "kommentar": neu_kommentar}])
    st.divider()
    for x in words:
        col = st.columns([2,5,5,5,2])
        if st.session_state.edit == x["_id"]:
            with col[1]:
                de  =st.text_input("deutsch", x["de"], label_visibility='hidden', key = f"de_{x['_id']}")
            with col[2]:
                en = st.text_input("englisch", x["en"], label_visibility='hidden', key = f"en_{x['_id']}")
            with col[3]:
                kommentar = st.text_input('kommentar', x["kommentar"], label_visibility='hidden', key = f"kommentar_{x['_id']}")
            with col[0]:
                st.write(" ")
                st.write(" ")
                save = st.button("Speichern", use_container_width=True, key = f"save_{x['_id']}")
                if save:
                    collection.update_one({"_id": st.session_state.edit}, { "$set" : { "de" : de, "en": en, "kommentar": kommentar}})
                    st.session_state.edit = ""
                    st.toast("Erfolgreich gespeichert!")
                    time.sleep(0.5)
                    st.rerun()
        else:
            with col[0]:
                edit = st.button("Bearbeiten", use_container_width=True, key = f"edit_{x['_id']}")
                if edit:
                    st.session_state.edit = x["_id"]
                    st.rerun()
            with col[1]:
                st.write(x["de"])
            with col[2]:
                st.write(x["en"])
            with col[3]:
                st.write(x["kommentar"])
            with col[4]:
                with st.popover('Löschen', use_container_width=True):
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{x['_id']}")
                    if submit: 
                        tools.delete_item_update_dependent_items(collection, x["_id"])
                    with colu3: 
                        st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")



            
else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
