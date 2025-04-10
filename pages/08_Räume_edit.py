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

# load css styles
from misc.css_styles import init_css
init_css()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.raum

new_entry = False

#geb = list(util.gebaeude.find({"sichtbar": True}, sort=[("rang", pymongo.ASCENDING)]))
geb = list(util.gebaeude.find({"sichtbar": True}, sort=[("name_de", pymongo.ASCENDING)]))
gebaeude_sichtbar = [ x["_id"]  for x in geb ]

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Räume")

    # check if entry can be found in database
    if st.session_state.edit == "new":
        new_entry = True
        x = st.session_state.new[collection]
        x["_id"] = "new"
    else:
        x = collection.find_one({"_id": st.session_state.edit})
        st.subheader(tools.repr(collection, x["_id"]))

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück ohne Speichern"):
            switch_page("Räume")
    with col2:
        with st.popover('Raum löschen'):
            if not new_entry:
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
        sichtbar = st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == util.leer[collection] else False))
        name_de=st.text_input('Name (de)', x["name_de"], disabled = (True if x["_id"] == util.leer[collection] else False))
        name_en=st.text_input('Name (en)', x["name_en"])
        kurzname=st.text_input('Kurzname', x["kurzname"])
        if x["gebaeude"] not in gebaeude_sichtbar:
            gebaeude_sichtbar.insert(0, x["gebaeude"])
        index = [g for g in gebaeude_sichtbar].index(x["gebaeude"])
        gebaeude1 = st.selectbox("Gebäude", [x for x in gebaeude_sichtbar], index = index, format_func = (lambda a: tools.repr(util.gebaeude, a)))
        raum=st.text_input('Raum', x["raum"])
        groesse=st.number_input('Groesse', value = x["groesse"], min_value = 0)
        kommentar=st.text_area('Kommentar', x["kommentar"])
        x_updated = ({"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "gebaeude": gebaeude1, "raum": raum, "groesse": groesse, "sichtbar": sichtbar, "kommentar": kommentar})
        submit = st.form_submit_button('Speichern', type = 'primary')
        if submit:
            if new_entry:
                tools.new(collection, ini = x_updated, switch=False)
            else:
                tools.update_confirm(collection, x, x_updated, )
            time.sleep(2)
            st.session_state.edit = ""
            switch_page("Räume")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)




