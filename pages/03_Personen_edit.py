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
from misc.util import logger
import misc.tools as tools

# load css styles
from misc.css_styles import init_css
init_css()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.person

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Personen")
    x = collection.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(collection, x["_id"], False))
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück ohne Speichern"):
            switch_page("Personen")
    with col2:
        with st.popover('Person löschen'):
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
        sichtbar = True #st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == util.leer[collection] else False))
        hp_sichtbar = st.checkbox("Auf Homepages sichtbar", x["hp_sichtbar"])
        name=st.text_input('Name (de)', x["name"], disabled = (True if x["_id"] == util.leer[collection] else False))
        vorname=st.text_input('Vorname', x["vorname"])
        name_prefix=st.text_input('Abkürzung des Vornamens', x["name_prefix"])
        titel=st.text_input('Titel', x["titel"])
        tel=st.text_input('Telefonnummer', x["tel"])
        email=st.text_input('Email', x["email"])
        st.write("Semester")
        semester_list = st.multiselect("Semester", [x["_id"] for x in util.semester.find(sort = [("kurzname", pymongo.DESCENDING)])], x["semester"], format_func = (lambda a: tools.repr(util.semester, a, False, True)), placeholder = "Bitte auswählen")
        se = list(util.semester.find({"_id": {"$in": semester_list}}, sort=[("rang", pymongo.ASCENDING)]))
        semester_list = [s["_id"] for s in se]
        x_updated = ({"name": name, "vorname": vorname, "name_prefix": name_prefix, "titel": titel, "tel": tel, "email": email, "sichtbar": sichtbar, "hp_sichtbar": hp_sichtbar, "semester": semester_list})
        submit = st.form_submit_button('Speichern', type = 'primary')
        if submit:
            tools.update_confirm(collection, x, x_updated, )
            time.sleep(2)
            st.session_state.edit = ""
            switch_page("personen")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
