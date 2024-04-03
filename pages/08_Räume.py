import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
import misc.util as util
import misc.tools as tools

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.raum
if st.session_state.page != "Räume":
    st.session_state.edit = ""
st.session_state.page = "Räume"

# Ändert die Ansicht. 
def edit(id):
    st.session_state.page = "Räume"
    st.session_state.edit = id

geb = list(util.gebaeude.find({"sichtbar": True}, sort=[("rang", pymongo.ASCENDING)]))
gebaeude_sichtbar = [ x["_id"]  for x in geb ]

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Räume")
    if st.session_state.edit == "" or st.session_state.page != "Räume":
        st.write("Mit 😎 markierte Räume sind in Auswahlmenüs sichtbar.")
        st.write(" ")
        co1, co2, co3 = st.columns([1,1,23]) 
        with co3:
            if st.button('**Neuen Raum hinzufügen**'):
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
        st.button('zurück zur Übersicht', key=f'edit-{x["_id"]}', on_click = edit, args = ("" ))
        st.subheader(repr(collection, x["_id"]))
        with st.popover('Raum löschen'):
            s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
            if s:
                st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
            else:
                st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
            colu1, colu2, colu3 = st.columns([1,1,1])
            with colu1:
                st.button(label = "Ja", type = 'primary', on_click = tools.delete_item_update_dependent_items, args = (collection, x["_id"]), key = f"delete-{x['_id']}")
            with colu3: 
                st.button(label="Nein", on_click = tools.reset, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
        with st.form(f'ID-{x["_id"]}'):
            sichtbar = st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == util.leer[collection] else False))
            name_de=st.text_input('Name (de)', x["name_de"], disabled = (True if x["_id"] == util.leer[collection] else False))
            name_en=st.text_input('Name (en)', x["name_en"])
            kurzname=st.text_input('Kurzname', x["kurzname"])
            if x["gebaeude"] not in gebaeude_sichtbar:
                gebaeude_sichtbar.insert(0, x["gebaeude"])
            index = [g for g in gebaeude_sichtbar].index(x["gebaeude"])
            gebaeude1 = st.selectbox("Gebäude", [x for x in gebaeude_sichtbar], index = index, format_func = (lambda a: repr(util.gebaeude, a)))
            raum=st.text_input('Raum', x["raum"])
            groesse=st.number_input('Groesse', value = x["groesse"], min_value = 0)
            kommentar=st.text_area('Kommentar', x["kommentar"])
            x_updated = ({"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "gebaeude": gebaeude1, "raum": raum, "groesse": groesse, "sichtbar": sichtbar, "kommentar": kommentar})
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

st.sidebar.button("logout", on_click = tools.logout)




