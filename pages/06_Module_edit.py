import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
import misc.util as util
import misc.tools as tools

# load css styles
from misc.css_styles import init_css
init_css()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.modul

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Module")
    x = collection.find_one({"_id": st.session_state.edit})
    st.subheader(tools.repr(collection, x["_id"], False))
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.popover('Modul löschen'):
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
    with col2:
        st.markdown('<span id="align-right"><\span>', unsafe_allow_html=True)
        if st.button("Zurück ohne Speichern"):
            switch_page("Module")

    with st.form(f'ID-{x["_id"]}'):
        sichtbar = st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == util.leer[collection] else False))
        name_de=st.text_input('Name (de)', x["name_de"], disabled = (True if x["_id"] == util.leer[collection] else False))
        name_en=st.text_input('Name (en)', x["name_en"])
        kurzname=st.text_input('Kurzname', x["kurzname"])
        kommentar=st.text_input('Kommentar', x["kommentar"])
        st.write("Studiengänge")
        stu_list = st.multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"$or": [{"sichtbar": True}, {"_id": {"$in": x["studiengang"]}}]}, sort = [("rang", pymongo.ASCENDING)])], x["studiengang"], format_func = (lambda a: tools.repr(util.studiengang, a, False)), placeholder = "Bitte auswählen")
        stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("rang", pymongo.ASCENDING)]))
        stu_list = [s["_id"] for s in stu]
        x_updated = ({"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "sichtbar": sichtbar, "kommentar": kommentar, "studiengang": stu_list})
        submit = st.form_submit_button('Speichern', type = 'primary')
        if submit:
            tools.update_confirm(collection, x, x_updated, )
            time.sleep(2)
            st.session_state.edit = ""
            switch_page("module")           

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
