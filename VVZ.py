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
collection = veranstaltung
if st.session_state.page != "Veranstaltung":
    st.session_state.edit = ""


# Ändert die Ansicht. 
def edit(id):
    st.session_state.page = "Veranstaltung"
    st.session_state.edit = id

def name_of_sem_id(semester_id):
    x = semester.find_one({"_id": semester_id})
    return x["name_de"]

def name_of_ver_id(ver_id):
    x = veranstaltung.find_one({"_id": ver_id})
    return x["name_de"]

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    st.header("Veranstaltungen")
    if st.session_state.edit == "" or st.session_state.page != "Veranstaltung":
        semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.semester = semesters[0]["_id"]
        sem_id = st.selectbox(label="Semester", options = [x["_id"] for x in semesters], index = 0, format_func = name_of_sem_id, placeholder = "Wähle ein Semester", label_visibility = "collapsed")
        st.session_state.semester = sem_id

        submit = False
        if sem_id is not None:
            kat = list(kategorie.find({"semester": sem_id}, sort=[("rang", pymongo.ASCENDING)]))
            for k in kat:
                st.write(k["prefix_de"])
                st.write(k["titel_de"])
                ver = list(veranstaltung.find({"kategorie": k["_id"]},sort=[("rang", pymongo.ASCENDING)]))
                for v in ver:
                    col1, col2, col3 = st.columns([1,1,23]) 
                    with col1:
                        st.button('↓', key=f'down-{v["_id"]}', on_click = tools.move_down, args = (collection, v,{"kategorie": v["kategorie"]}, ))
                    with col2:
                        st.button('↑', key=f'up-{v["_id"]}', on_click = tools.move_up, args = (collection, v, {"kategorie": v["kategorie"]},))
                    with col3:
                        d = [(person.find_one({"_id": x}))["name"] for x in v["dozent"]]
                        s = f"{v['name']} ({', '.join(d)})"
                        st.button(s, key=f"edit-{v['_id']}", on_click = edit, args = (v["_id"], ))
    else:
        x = veranstaltung.find_one({"_id": st.session_state.edit})
        st.button('zurück zur Übersicht', key=f'edit-{x["_id"]}', on_click = edit, args = ("", ))
        st.subheader(repr(collection, x["_id"]))
        with st.form(f'ID-{x["_id"]}'):
            hp_sichtbar = st.checkbox("Auf Homepages sichtbar", x["hp_sichtbar"])
            name_de=st.text_input('Name (de)', x["name_de"])
            name_en=st.text_input('Name (en)', x["name_en"])
            midname_de=st.text_input('Mittelkurzer Name (de)', x["midname_de"])
            midname_en=st.text_input('Mittelkurzer Name (en)', x["midname_en"])
            kurzname_en=st.text_input('Kurzname', x["kurzname"])
            kat = [g["_id"] for g in list(kategorie.find({"semester": x["semester"]}))]
            index = [g for g in kat].index(x["kategorie"])
            kategorie = st.selectbox("Kategorie", [x for x in kat], index = index, format_func = (lambda a: repr(kategorie, a)))

            st.write("Codes")
            co = list(code.find({"semester": x["semester"]}, sort = [("rang", pymongo.ASCENDING)]))
            code_dict = {}
            for c in co:
                code_dict[c["_id"]] = f"{c['beschreibung_de']} ({c['name']})"
            code_list = tools.update_list(code_dict, x["code"], no_cols = 2, all_choices = True, id = x["_id"])
 

            ects_en=st.text_input('ECTS', x["ects"])
            url_en=st.text_input('URL', x["url"])

            inhalt_de = st.text_area('Inhalt (de)', x["inhalt_de"])
            inhalt_en = st.text_area('Inhalt (en)', x["inhalt_en"])
            literatur_de = st.text_area('Literatur (de)', x["literatur_de"])
            literatur_en = st.text_area('Literatur (en)', x["literatur_en"])
            vorkenntnisse_de = st.text_area('Vorkenntnisse (de)', x["vorkenntnisse_de"])
            vorkenntnisse_en = st.text_area('Vorkenntnisse (en)', x["vorkenntnisse_en"])
            kommentar_latex_de = st.text_area('Kommentar (Latex, de)', x["kommentar_latex_de"])
            kommentar_latex_en = st.text_area('Kommentar (Latex, en)', x["kommentar_latex_en"])
            kommentar_html_de = st.text_area('Kommentar (HTML, de)', x["kommentar_html_de"])
            kommentar_html_en = st.text_area('Kommentar (HTML, en)', x["kommentar_html_en"])

            pe = list(person.find({"sichtbar": True, "semester": { "$elemMatch": { "$eq": x["semester"]}}}, sort = [("rang", pymongo.ASCENDING)]))
            per_dict = {}
            for p in pe:
                per_dict[p["_id"]] = repr(person, p["_id"], show_collection = False)

            st.write("Dozent*innen")
            per_list = tools.update_list(per_dict, x["dozent"], no_cols = 4, all_choices = False, id = f"{x['_id']}-dozent")
            st.write("Assistent*innen")
            per_list = tools.update_list(per_dict, x["assistent"], no_cols = 4, all_choices = False, id = f"{x['_id']}-assistent")
            st.write("Organisation")
            per_list = tools.update_list(per_dict, x["organisation"], no_cols = 4, all_choices = False, id = f"{x['_id']}-orga")
 



#            "verwendbarkeit_modul", "verwendbarkeit_anforderung", "verwendbarkeit",            "woechentlicher_termin", "einmaliger_termin",

 


        



#    if submit:
#        reset()
#        st.rerun()

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
