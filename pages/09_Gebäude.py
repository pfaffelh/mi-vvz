import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
from misc.util import *
import misc.tools as tools

# make all neccesary variables available to session_state
setup_session_state()

# Navigation in Sidebar anzeigen
display_navigation()

# Es geht hier vor allem um diese Collection:
collection = gebaeude
if st.session_state.page != "Gebäude":
    st.session_state.edit = ""

# Ändert die Ansicht. 
def edit(id):
    st.session_state.page = "Gebäude"
    st.session_state.edit = id

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Gebäude")
    if st.session_state.edit == "" or st.session_state.page != "Gebäude":
        st.write("Mit 😎 markierte Gebäude sind in Auswahlmenüs sichtbar.")
        st.write(" ")
        co1, co2, co3 = st.columns([1,1,23]) 
        with co3:
            if st.button('**Neues Gebäude hinzufügen**'):
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
                st.button(abk, key=f"edit-{x['_id']}", on_click = edit, args = (x["_id"], ))
    else:
        x = collection.find_one({"_id": st.session_state.edit})
        st.button('zurück zur Übersicht', key=f'edit-{x["_id"]}', on_click = edit, args = ("", ))
        st.subheader(repr(collection, x["_id"]))
        with st.popover('Gebäude löschen'):
            s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
            if s:
                st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
            else:
                st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
            colu1, colu2, colu3 = st.columns([1,1,1])
            with colu1:
                st.button(label = "Ja", type = 'primary', on_click = tools.delete_item_update_dependent_items, args = (collection, x["_id"]), key = f"delete-{x['_id']}")
            with colu3: 
                st.button(label="Nein", on_click = reset, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
        with st.form(f'ID-{x["_id"]}'):
            sichtbar = st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == leer[collection] else False))
            name_de=st.text_input('Name (de)', x["name_de"], disabled = (True if x["_id"] == leer[collection] else False))
            name_en=st.text_input('Name (en)', x["name_en"])
            kurzname=st.text_input('Kurzname', x["kurzname"])
            adresse=st.text_input('Adresse', x["adresse"])
            url=st.text_input('Url', x["url"])
            kommentar=st.text_area('Kommentar', x["kommentar"])
            x_updated = ({"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "adresse": adresse, "url": url, "sichtbar": sichtbar, "kommentar": kommentar})
            submit = st.form_submit_button('Speichern', type = 'primary')
            if submit:
                tools.update_confirm(collection, x, x_updated, )
                time.sleep(2)
                st.session_state.expanded = ""
                st.session_state.edit = ""
                st.rerun()                      

#    if submit:
#        reset()
#        st.rerun()

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)



