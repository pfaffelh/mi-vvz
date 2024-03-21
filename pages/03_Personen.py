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
collection = person
if st.session_state.page != "Person":
    st.session_state.edit = ""

# Die Semesterliste für die Semester, an denen die Person da ist/war.
se = list(semester.find({}, sort = [("kurzname", pymongo.DESCENDING)]))
sem_dict = {}
for s in se:
    sem_dict[s["_id"]] = s["kurzname"]

# Ändert die Ansicht. 
def edit(id):
    st.session_state.page = "Person"
    st.session_state.edit = id

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Personen")
    if st.session_state.edit == "" or st.session_state.page != "Person":
        st.write("**Fettgrdruckte** Personen sind in Auswahlmenüs sichtbar.")
        st.write(" ")
        co1, co2, co3 = st.columns([1,1,23]) 
        with co3:
            if st.button('**Neue Person hinzufügen**'):
                tools.new(collection)

        y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))
        for x in y:
            co1, co2, co3 = st.columns([1,1,23]) 
            with co1: 
                st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
            with co2:
                st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
            with co3:
                abk = f"{x['name'].strip()}, {x['vorname'].strip()}"
                abk = f"**{abk.strip()}**" if x["sichtbar"] else f"{abk.strip()}"
                st.button(abk, key=f"edit-{x['_id']}", on_click = edit, args = (x["_id"], ))
    else:
        x = collection.find_one({"_id": st.session_state.edit})
        st.button('zurück zur Übersicht', key=f'edit-{x["_id"]}', on_click = edit, args = ("", ))
        with st.form(f'ID-{x["_id"]}'):
            sichtbar = st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == leer[collection] else False))
            hp_sichtbar = st.checkbox("Auf Homepages sichtbar", x["hp_sichtbar"])
            name=st.text_input('Name (de)', x["name"], disabled = (True if x["_id"] == leer[collection] else False))
            vorname=st.text_input('Vorname', x["vorname"])
            name_prefix=st.text_input('Abkürzung des Vornamens', x["name_prefix"])
            titel=st.text_input('Titel', x["titel"])
            tel=st.text_input('Telefonnummer', x["tel"])
            email=st.text_input('Email', x["email"])
            st.write("Semester")
            semester_list = tools.update_list(sem_dict, x["semester"], no_cols = 8, all_choices = True, id = x["_id"])
            x_updated = ({"name": name, "vorname": vorname, "name_prefix": name_prefix, "titel": titel, "tel": tel, "email": email, "sichtbar": sichtbar, "hp_sichtbar": hp_sichtbar, "semester": semester_list})
            col1, col2, col3 = st.columns([1,7,1]) 
            with col1: 
                submit = st.form_submit_button('Speichern', type = 'primary')
            if submit:
                tools.update_confirm(collection, x, x_updated, )
                time.sleep(2)
                st.session_state.expanded = ""
                st.session_state.edit = ""
                st.rerun()                      
            with col3: 
                deleted = st.form_submit_button("Löschen")
            if deleted:
                st.session_state.submitted = True
                st.session_state.expanded = x["_id"]
                st.session_state.edit = x["_id"]
            if st.session_state.submitted and st.session_state.expanded == x["_id"]:
                with col1: 
                    st.form_submit_button(label = "Ja", type = 'primary', on_click = tools.delete_item_update_dependent_items, args = (collection, x["_id"]))
                with col2: 
                    s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
                    if s:
                        st.warning("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
                    else:
                        st.warning("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                with col3: 
                    st.form_submit_button(label="Nein", on_click = reset, args=("Nicht gelöscht!",))

#    if submit:
#        reset()
#        st.rerun()

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
