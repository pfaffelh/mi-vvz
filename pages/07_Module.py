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
collection = modul
if st.session_state.page != "Modul":
    st.session_state.edit = ""

# Die Semesterliste für die Semester, an denen die Person da ist/war.
stud = list(studiengang.find({"sichtbar": True}, sort = [("kurzname", pymongo.DESCENDING)]))
stu_dict = {}
for s in stud:
    stu_dict[s["_id"]] = f"{s['kurzname']}"

# Ändert die Ansicht. 
def edit(id):
    st.session_state.page = "Modul"
    st.session_state.edit = id

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Module")
    if st.session_state.edit == "" or st.session_state.page != "Modul":
        st.write("**Fettgrdruckte** Module sind in Auswahlmenüs sichtbar.")
        st.write(" ")
        co1, co2, co3 = st.columns([1,1,23]) 
        with co3:
            if st.button('**Neues Modul hinzufügen**'):
                tools.new(collection)

        y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))
        for x in y:
            co1, co2, co3 = st.columns([1,1,23]) 
            with co1: 
                st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
            with co2:
                st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
            with co3:
                abk = f"{x['name_de'].strip()} ({x['kurzname'].strip()})"
                abk = f"**{abk.strip()}**" if x["sichtbar"] else f"{abk.strip()}"
                st.button(abk, key=f"edit-{x['_id']}", on_click = edit, args = (x["_id"], ))
    else:
        x = collection.find_one({"_id": st.session_state.edit})
        st.button('zurück zur Übersicht', key=f'edit-{x["_id"]}', on_click = edit, args = ("", ))
        with st.form(f'ID-{x["_id"]}'):
            sichtbar = st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == leer[collection] else False))
            name_de=st.text_input('Name (de)', x["name_de"], disabled = (True if x["_id"] == leer[collection] else False))
            name_en=st.text_input('Name (en)', x["name_en"])
            kurzname=st.text_input('Kurzname', x["kurzname"])
            kommentar=st.text_input('Kommentar', x["kommentar"])
            st.write("Studiengänge")
            stu_list = tools.update_list(stu_dict, x["studiengang"], no_cols = 5, all_choices = True, id = x["_id"])
            x_updated = ({"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "sichtbar": sichtbar, "kommentar": kommentar, "studiengang": stu_list})
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
