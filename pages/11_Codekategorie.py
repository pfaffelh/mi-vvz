import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
import pandas as pd

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

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.codekategorie

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Kategorie von Codes")
    st.write("Mit 😎 gekennzeichnete Semester sind auf www.studium.math... sichtbar.")
    st.write(" ")
    st.write("### Kategorie von Codes")
    st.write('Dies ist z.B. "Sprache". Dann kann in den Codes dieser Codekategorie so etwas stehen wie "Vorlesung in englischer Sprache". Ein anderes Beispiel ist eine Codekategorie "Evaluation". Hier könnte eine Code angeben, ob die entsprechende Veranstaltung evaluiert werden soll.' )
    collection = util.codekategorie

    st.write("Mit 😎 markierte Codekategorien sind auf der Homepage sichtbar.")
    st.write(" ")
    if st.button('**Neue Codekategorie hinzufügen**'):
        tools.new(collection, switch = False)

    y = list(collection.find({}, sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:   
            abk = f"{x['name_de'].strip()}"
            abk = f"{abk.strip()} 😎" if x["hp_sichtbar"] else f"{abk.strip()}"
            with st.expander(abk, (True if x["_id"] == st.session_state.edit else False)):
                with st.popover('Codekategorie löschen'):
                    s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
                    if s:
                        st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
                    else:
                        st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
                    if submit:
                        tools.delete_item_update_dependent_items(collection, x["_id"], False)
                        st.rerun()
                    with colu3: 
                        st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")

                with st.form(f'ID-{x["_id"]}'):
                    hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar {'😎' if x['hp_sichtbar'] else ''}", value = x["hp_sichtbar"], key=f'ID-{x["_id"]}-hp_sichtbar')
                    name_de=st.text_input('Titel (de)', x["name_de"], key=f'titel-de-{x["_id"]}')
                    name_en=st.text_input('Titel (en)', x["name_en"], key=f'titel-en-{x["_id"]}')
                    beschreibung_de=st.text_input('Beschreibung (de)', x["beschreibung_de"], key=f'beschreibung-de-{x["_id"]}')
                    beschreibung_en=st.text_input('Beschreibung (en)', x["beschreibung_en"], key=f'beschreibung-en-{x["_id"]}')
                    kommentar=st.text_area('Kommentar', x["kommentar"])
                    code = []
                    x_updated = {"hp_sichtbar": hp_sichtbar, "name_de": name_de, "name_en": name_en, "beschreibung_de": beschreibung_de, "kommentar": kommentar, "code": []}
                    submit = st.form_submit_button('Speichern', type = 'primary')
                    if submit:
                        tools.update_confirm(collection, x, x_updated, )
                        time.sleep(2)
                        st.session_state.edit = ""
                        st.rerun()                      


else:
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
