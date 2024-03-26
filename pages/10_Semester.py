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
collection = semester
if st.session_state.page != "Semester":
    st.session_state.edit = ""

def reset_and_confirm(text=None):
    st.session_state.submitted = False 
    st.session_state.expanded = ""
    if text is not None:
        st.success(text)

def semester_delete_confirm_one(x):
    semester.delete_one(x)
    # alle Personen updaten, Semester wegnehmen
    # alle Kategorien und Codes für dieses Semester löschen
    # alle Veranstaltungen in diesem Semester löschen
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Semester {x['name_de']} gelöscht.")
    st.success("Erfolgreich gelöscht!")

def kategorie_delete_confirm_one(x):
    kategorie.delete_one(x)
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Kategorie {x['titel_de']} gelöscht.")
    st.success("Erfolgreich gelöscht!")

def code_delete_confirm_one(x):
    code.delete_one(x)
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Code {x['name']} gelöscht.")
    st.success("Erfolgreich gelöscht!")

def semester_update_confirm(x, x_updated):
    semester.update_one(x, {"$set": x_updated })
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Semester {x['name_de']} geändert.")
    st.success("Erfolgreich geändert!")

def kategorie_update_confirm(x, x_updated):
    kategorie.update_one(x, {"$set": x_updated })
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Kategorie {x['titel_de']} geändert.")
    st.success("Erfolgreich geändert!")

def code_update_confirm(x, x_updated):
    code.update_one(x, {"$set": x_updated })
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Code {x['name']} geändert.")
    st.success("Erfolgreich geändert!")

def kategorie_move_up(x):
    target = kategorie.find_one( {"semester": st.session_state["semester"], "rang": {"$lt": x["rang"]}}, sort = [("rang",-1)])
    if target:
        n= target["rang"]
        kategorie.update_one(target, {"$set": {"rang": x["rang"]}})    
        kategorie.update_one(x, {"$set": {"rang": n}})    

def kategorie_move_down(x):
    target = kategorie.find_one({"semester": st.session_state["semester"], "rang": {"$gt": x["rang"]}}, sort = [("rang",+1)])
    if target:
        n= target["rang"]
        kategorie.update_one(target, {"$set": {"rang": x["rang"]}})    
        kategorie.update_one(x, {"$set": {"rang": n}})    

def code_move_up(x):
    target = code.find_one( {"semester": st.session_state["semester"], "rang": {"$lt": x["rang"]}}, sort = [("rang",-1)])
    if target:
        n= target["rang"]
        code.update_one(target, {"$set": {"rang": x["rang"]}})    
        code.update_one(x, {"$set": {"rang": n}})    

def code_move_down(x):
    target = code.find_one({"semester": st.session_state["semester"], "rang": {"$gt": x["rang"]}}, sort = [("rang",+1)])
    if target:
        n= target["rang"]
        code.update_one(target, {"$set": {"rang": x["rang"]}})    
        code.update_one(x, {"$set": {"rang": n}})    

def name_of_id(semester_id):
    x = semester.find_one({"_id": semester_id})
    res = x["name_de"]
    if x["hp_sichtbar"]:
        res = f"{res.strip()} 😎"
    return res

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Semester-Grundeinstellungen")
    st.write("Mit 😎 gekennzeichnete Semester sind auf www.studium.math... sichtbar.")
    st.write(" ")
    if st.button('**Neues Semester hinzufügen**'):
        # TODO
        pass

    semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
    st.session_state.semester = semesters[0]["_id"]

    sem_id = st.selectbox(label="Semester", options = [x["_id"] for x in semesters], index = 0, format_func = name_of_id, placeholder = "Wähle ein Semester", label_visibility = "collapsed")
    st.session_state.semester = sem_id

    submit = False
    sem = semester.find_one({"_id": sem_id})

    with st.form(f'ID-{sem["_id"]}'):
        name_de = st.text_input('Name (de)', sem["name_de"])
        name_en = st.text_input('Name (en)', sem["name_en"])
        kurzname = st.text_input('Kurzname', sem["kurzname"])
        hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar {'😎' if sem['hp_sichtbar'] else ''}", value = sem["hp_sichtbar"], key=f'ID-{sem["_id"]}-hp_sichtbar')
        sem_updated = {"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "hp_sichtbar": hp_sichtbar}
        col1, col2, col3 = st.columns([1,7,1]) 
        with col1: 
            submit = st.form_submit_button('Speichern', type = 'primary')
        if submit:
            tools.update_confirm(collection, sem, sem_updated, )
            time.sleep(2)
            st.session_state.expanded = ""
            st.session_state.edit = ""
            st.rerun()                      
        with col3: 
            deleted = st.form_submit_button("Löschen")
        if deleted:
            st.session_state.submitted = True
            st.session_state.expanded = sem["_id"]
            st.session_state.edit = sem["_id"]
        if st.session_state.submitted and st.session_state.expanded == sem["_id"]:
            with col1: 
                st.form_submit_button(label = "Ja", type = 'primary', on_click = tools.delete_semester, args = (sem["_id"],))
            with col2: 
                s = ("  \n".join(tools.find_dependent_items(collection, sem["_id"])))
                if s:
                    st.warning("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch gelöscht!")
                else:
                    st.warning("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
            with col3: 
                st.form_submit_button(label="Nein", on_click = reset, args=("Nicht gelöscht!",))

    st.write("### Kategorien")
    collection = kategorie

    st.write("Mit 😎 markierte Kategorien sind auf der Homepage sichtbar.")
    st.write(" ")
    if st.button('**Neue Kategorie hinzufügen**'):
        st.write(semester.find_one({"_id": st.session_state.semester})["_id"])
        tools.new(collection, ini = { "semester": st.session_state.semester })

    y = list(collection.find({ "semester": st.session_state.semester }, sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:   
            abk = f"{x['titel_de'].strip()}"
            abk = f"{abk.strip()} 😎" if x["hp_sichtbar"] else f"{abk.strip()}"
            with st.expander(abk, (True if x["_id"] == st.session_state.expanded else False)):
                with st.form(f'ID-{x["_id"]}'):
                    hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar {'😎' if sem['hp_sichtbar'] else ''}", value = x["hp_sichtbar"], key=f'ID-{x["_id"]}-hp_sichtbar')
                    titel_de=st.text_input('Titel (de)', x["titel_de"], key=f'titel-de-{x["_id"]}')
                    titel_en=st.text_input('Titel (en)', x["titel_en"], key=f'titel-en-{x["_id"]}')
                    untertitel_de=st.text_input('Untertitel (de)', x["untertitel_de"], key=f'untertitel-de-{x["_id"]}')
                    untertitel_en=st.text_input('Untertitel (en)', x["untertitel_en"], key=f'untertitel-en-{x["_id"]}')
                    prefix_de=st.text_area('Prefix (de)', x["prefix_de"], key=f'prefix-de-{x["_id"]}')
                    prefix_en=st.text_area('Prefix (en)', x["prefix_en"], key=f'prefix-en-{x["_id"]}')
                    suffix_de=st.text_area('Prefix (de)', x["suffix_de"], key=f'suffix-de-{x["_id"]}')
                    suffix_en=st.text_area('Prefix (en)', x["suffix_en"], key=f'suffix-en-{x["_id"]}')
                    kommentar=st.text_area('Kommentar', x["kommentar"])
                    x_updated = {"hp_sichtbar": hp_sichtbar, "titel_de": titel_de, "titel_en": titel_en, "untertitel_de": untertitel_de, "untertitel_en": untertitel_en, "prefix_de": prefix_de, "prefix_en": prefix_en, "suffix_de": suffix_de, "suffix_en": suffix_en, "kommentar": kommentar}
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


    st.write("### Codes")
    collection = code
    st.write("Mit 😎 markierte Codes sind auf der Homepage sichtbar.")
    st.write(" ")
    if st.button('**Neuen Code hinzufügen**'):
        tools.new(collection, ini = { "semester": st.session_state.semester })

    y = list(collection.find({ "semester": st.session_state.semester }, sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:   
            abk = f"{x['beschreibung_de'].strip()}, {x['name'].strip()}"
            abk = f"{abk.strip()} 😎" if x["hp_sichtbar"] else f"{abk.strip()}"
            with st.expander(abk, (True if x["_id"] == st.session_state.expanded else False)):
                with st.form(f'ID-{x["_id"]}'):
                    hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar {'😎' if sem['hp_sichtbar'] else ''}", value = x["hp_sichtbar"], key=f'ID-{x["_id"]}-hp_sichtbar')
                    name=st.text_input('Name', x["name"], key=f'name-{x["_id"]}')
                    beschreibung_de=st.text_input('Beschreibung (de)', x["beschreibung_de"], key=f'beschreibung-de-{x["_id"]}')
                    beschreibung_en=st.text_input('Beschreibung (en)', x["beschreibung_en"], key=f'beschreibung-en-{x["_id"]}')
                    kommentar=st.text_area('Kommentar', x["kommentar"])
                    x_updated = {"hp_sichtbar": hp_sichtbar, "name": name, "beschreibung_de": beschreibung_de, "beschreibung_en": beschreibung_en, "kommentar": kommentar}
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



else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
