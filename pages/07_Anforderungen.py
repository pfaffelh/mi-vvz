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

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.anforderung

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Anforderungen")
    st.write("Mit 😎 markierte Anforderungen sind in Auswahlmenüs sichtbar.")
    st.write(" ")
    co1, co2, co3 = st.columns([1,1,23]) 
    with co3:
        if st.button('**Neue Anforderung hinzufügen**'):
            st.session_state.edit = "new"
            switch_page("anforderungen edit")

    y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:
            an = util.anforderungkategorie.find_one({"_id": x["anforderungskategorie"]})["name_de"]
            abk = f"{x['name_de'].strip()} ({an.strip()})"
            abk = f"{abk.strip()} 😎" if x["sichtbar"] else f"{abk.strip()}"
            submit = st.button(abk, key=f"edit-{x['_id']}")
        if submit:
            st.session_state.edit = x["_id"]
            switch_page("anforderungen edit")

    st.subheader("Anforderungskategorien")
    collection = util.anforderungkategorie
    st.write("Mit 😎 markierte Anforderungkategorien sind in Auswahlmenüs sichtbar.")
    st.write(" ")
    if st.button('**Neue Anforderungskategorie hinzufügen**'):
        tools.new(collection)

    y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:   
            abk = f"{x['name_de'].strip()}"
            abk = f"{abk.strip()} 😎" if x["sichtbar"] else f"{abk.strip()}"
            with st.expander(abk, (True if x["_id"] == st.session_state.expanded else False)):
                st.subheader(tools.repr(collection, x["_id"]))
                with st.popover('Anforderungskategorie löschen'):
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
                        st.button(label="Nein", on_click = tools.reset_vars, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
                with st.form(f'ID-{x["_id"]}'):
                    sichtbar = st.checkbox("In Auswahlmenüs sichtbar", value = x["sichtbar"], key=f'ID-{x["_id"]}-sichtbar')
                    name_de=st.text_input('Name (de)', x["name_de"], key=f'name_de-{x["_id"]}')
                    name_en=st.text_input('Name (en)', x["name_en"], key=f'name_en-{x["_id"]}')
                    kommentar=st.text_area('Kommentar', x["kommentar"])
                    x_updated = {"sichtbar": sichtbar, "name_de": name_de, "name_en": name_en,"kommentar": kommentar}
                    submit = st.form_submit_button('Speichern', type = 'primary')
                    if submit:
                        tools.update_confirm(collection, x, x_updated, )
                        time.sleep(2)
                        st.session_state.expanded = ""
                        st.session_state.edit = ""
                        st.rerun()

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
