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

# load css styles
from misc.css_styles import init_css
init_css()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.terminart

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Art von Terminen")
    x = collection.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(collection, x["_id"]))

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück ohne Speichern"):
            switch_page("terminart")
    with col2:
        with st.popover('Terminart löschen'):
            s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
            if s:
                st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
            else:
                st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
            colu1, colu2, colu3 = st.columns([1,1,1])
            with colu1:
                submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
            if submit:
                tools.delete_item_update_dependent_items(collection, x["_id"])
            with colu3: 
                st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
        

    with st.form(f'ID-{x["_id"]}'):
        hp_sichtbar = st.checkbox("Auf Homepage sichtbar", x["hp_sichtbar"], disabled = False)
        komm_sichtbar = st.checkbox("Im kommentierten VVZ sichtbar", x["komm_sichtbar"], disabled = False)
        name_de=st.text_input('Name (de)', x["name_de"])
        name_en=st.text_input('Name (en)', x["name_en"])
        x_updated = ({"name_de": name_de, "name_en": name_en, "hp_sichtbar": hp_sichtbar, "komm_sichtbar": komm_sichtbar})
        submit = st.form_submit_button('Speichern', type = 'primary')
        if submit:
            tools.update_confirm(collection, x, x_updated, )
            time.sleep(2)
            st.session_state.edit = ""
            switch_page("terminart")
            
else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)



