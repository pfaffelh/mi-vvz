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
collection = util.studiengang
if st.session_state.page != "Studiengang":
    st.session_state.edit = ""
st.session_state.page = "Studiengang"

# Die Semesterliste für die Semester, an denen die Person da ist/war.
mo = list(util.modul.find({"sichtbar": True}, sort = [("kurzname", pymongo.DESCENDING)]))
mod_dict = {}
for m in mo:
    mod_dict[m["_id"]] = f"{m['name_de']} ({m['kurzname']})"

# Ändert die Ansicht. 
def edit(id):
    st.session_state.page = "Studiengang"
    st.session_state.edit = id

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Studiengänge")
    if st.session_state.edit == "" or st.session_state.page != "Studiengang":
        st.write("Mit 😎 markierte Studiengänge sind in Auswahlmenüs sichtbar.")
        st.write(" ")
        co1, co2, co3 = st.columns([1,1,23]) 
        with co3:
            if st.button('**Neuen Studiengang hinzufügen**'):
                tools.new(collection)

        y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))
        for x in y:
            co1, co2, co3 = st.columns([1,1,23]) 
            with co1: 
                st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
            with co2:
                st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
            with co3:
                abk = f"{x['name'].strip()} ({x['kurzname'].strip()})"
                abk = f"{abk.strip()} 😎" if x["sichtbar"] else f"{abk.strip()}"
                st.button(abk, key=f"edit-{x['_id']}", on_click = edit, args = (x["_id"], ))
    else:
        x = collection.find_one({"_id": st.session_state.edit})
        st.button('zurück zur Übersicht', key=f'edit-{x["_id"]}', on_click = edit, args = ("", ))
        st.subheader(repr(collection, x["_id"], False))
        with st.popover('Studiengang löschen'):
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
            name=st.text_input('Name', x["name"], disabled = (True if x["_id"] == util.leer[collection] else False))
            kurzname=st.text_input('Kurzname', x["kurzname"])
            kommentar=st.text_input('Kommentar', x["kommentar"])
            modul_list = st.multiselect("Module", [x["_id"] for x in util.modul.find({"$or": [{"sichtbar": True}, {"_id": {"$in": x["modul"]}}]}, sort = [("rang", pymongo.ASCENDING)])], x["modul"], format_func = (lambda a: repr(util.modul, a, False)), placeholder = "Bitte auswählen")
            x_updated = ({"name": name, "kurzname": kurzname, "sichtbar": sichtbar, "kommentar": kommentar, "modul": modul_list})
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
