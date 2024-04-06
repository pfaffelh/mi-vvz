import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
import pandas as pd

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
collection = util.semester
if st.session_state.page != "Semester":
    st.session_state.edit = ""
st.session_state.page = "Semester"

def name_of_id(semester_id):
    x = util.semester.find_one({"_id": semester_id})
    res = x["name_de"]
    if x["hp_sichtbar"]:
        res = f"{res.strip()} 😎"
    return res

collection = util.semester
# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Semester-Grundeinstellungen")
    st.write("Mit 😎 gekennzeichnete Semester sind auf www.studium.math... sichtbar.")
    st.write(" ")
    x = util.semester.find_one({"_id": st.session_state.semester_id})

    with st.popover(f'{tools.repr(collection, st.session_state.semester_id, False, False)} löschen', help = "Dieses Semester wird in der Tat aus der Datenbank gelöscht!"):
        s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
        if s:
            st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
        else:
            st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
        colu1, colu2, colu3 = st.columns([1,1,1])
        with colu1:
            submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
        if submit:
            tools.delete_semester(st.session_state.semester_id)
            time.sleep(2)
            semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
            st.session_state.semester_id = semesters[0]["_id"]
            st.session_state.edit = ""
            st.rerun()
        with colu3: 
            st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
    with st.expander(f'{tools.repr(collection, st.session_state.semester_id, False, False)} kopieren'):
        st.write("Kopiere " + util.semester.find_one(x)["name_de"])
        new_name_de = st.text_input('Name der Kopie (de)', "")
        new_name_en = st.text_input('Name der Kopie (en)', "")
        new_kurzname = st.text_input('Kurzname der Kopie', "")
        new_hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar", value = False, key=f'kopie-hp_sichtbar')
        last_sem_kurzname = list(util.semester.find(sort = [("rang", pymongo.DESCENDING)]))[0]["kurzname"]
        kopiere_personen = st.checkbox(f"Alle im {last_sem_kurzname} beteiligten Personen ins kopierte Semester übernehmen?", value = True, key=f'kopie-person')
        x_updated = {"name_de": new_name_de, 
                     "name_en": new_name_en, 
                     "kurzname": new_kurzname, 
                     "hp_sichtbar": new_hp_sichtbar, 
                     "rubrik": [], 
                     "code": [], 
                     "veranstaltung": [], 
                     "rang": list(collection.find(sort = [("rang", pymongo.DESCENDING)]))[0]["rang"]+1
                     }
        st.write("Rubriken und Codes von Veranstaltungen werden übernommen, URLs nicht.")
        kat_list = list(util.rubrik.find({"semester": x["_id"]}, sort = [("rang", pymongo.ASCENDING)]))
        ver_list = []
        for k in kat_list:
            ver_list.extend(list(util.veranstaltung.find({"rubrik": k["_id"]}, sort = [("rang", pymongo.ASCENDING)])))
        kop_ver_list = st.multiselect("Zu kopierende Veranstaltungen", [v["_id"] for v in ver_list], [v["_id"] for v in ver_list], format_func = (lambda a: tools.repr(util.veranstaltung, a, False)))
        g = [{"_id": v, "Name": tools.repr(util.veranstaltung, v, False), "Personen": False, "Termine": False, "Kommentare": False, "Verwendbarkeit": True} for v in kop_ver_list]
        df = pd.DataFrame.from_records(g)
        df_new = st.data_editor(
            df, height = None, column_config = {"_id": None}, disabled=["Name"], hide_index = True)
        st.button("Kopieren", on_click=tools.kopiere_semester, args = (x["_id"], x_updated, df_new, kopiere_personen), type="primary")
    with st.form(f'ID-{x["_id"]}'):
        name_de = st.text_input('Name (de)', x["name_de"])
        name_en = st.text_input('Name (en)', x["name_en"])
        kurzname = st.text_input('Kurzname', x["kurzname"])
        hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar {'😎' if x['hp_sichtbar'] else ''}", value = x["hp_sichtbar"], key=f'ID-{x["_id"]}-hp_sichtbar')
        x_updated = {"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "hp_sichtbar": hp_sichtbar}
        submit = st.form_submit_button('Speichern', type = 'primary')
        if submit:
            tools.update_confirm(collection, x, x_updated, )
            time.sleep(2)
            st.session_state.edit = ""
            st.rerun()
    st.write("### Rubrik")
    collection = util.rubrik

    st.write("Mit 😎 markierte Rubriken sind auf der Homepage sichtbar.")
    st.write(" ")
    if st.button('**Neue Rubrik hinzufügen**'):
        tools.new(collection, ini = { "semester": st.session_state.semester_id }, switch = False)

    y = list(collection.find({ "semester": st.session_state.semester_id }, sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:   
            abk = f"{x['titel_de'].strip()}"
            abk = f"{abk.strip()} 😎" if x["hp_sichtbar"] else f"{abk.strip()}"
            with st.expander(abk, (True if x["_id"] == st.session_state.edit else False)):
                with st.popover('Rubrik löschen'):
                    s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
                    if s:
                        st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
                    else:
                        st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
                    if submit:
                        tools.delete_item_update_dependent_items(collection, x["_id"], False)
                        st.rerun()
                    with colu3: 
                        st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")

                with st.form(f'ID-{x["_id"]}'):
                    hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar {'😎' if x['hp_sichtbar'] else ''}", value = x["hp_sichtbar"], key=f'ID-{x["_id"]}-hp_sichtbar')
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
                    submit = st.form_submit_button('Speichern', type = 'primary')
                    if submit:
                        tools.update_confirm(collection, x, x_updated, )
                        time.sleep(2)
                        st.session_state.edit = ""
                        st.rerun()                      

    st.write("### Codes")
    collection = util.code
    st.write("Mit 😎 markierte Codes sind auf der Homepage sichtbar.")
    st.write(" ")
    if st.button('**Neuen Code hinzufügen**'):
        tools.new(collection, ini = { "semester": st.session_state.semester_id }, switch = False)

    y = list(collection.find({ "semester": st.session_state.semester_id }, sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:   
            abk = f"{x['beschreibung_de'].strip()}, {x['name'].strip()}"
            abk = f"{abk.strip()} 😎" if x["hp_sichtbar"] else f"{abk.strip()}"
            with st.expander(abk, (True if x["_id"] == st.session_state.edit else False)):
                st.subheader(tools.repr(collection, x["_id"]))
                with st.popover('Code löschen'):
                    s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
                    if s:
                        st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
                    else:
                        st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
                    if submit:
                        tools.delete_item_update_dependent_items(collection, x["_id"], False)
                        st.rerun()
                    with colu3: 
                        st.button(label="Nein", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
                with st.form(f'ID-{x["_id"]}'):
                    hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar {'😎' if x['hp_sichtbar'] else ''}", value = x["hp_sichtbar"], key=f'ID-{x["_id"]}-hp_sichtbar')
                    name=st.text_input('Name', x["name"], key=f'name-{x["_id"]}')
                    beschreibung_de=st.text_input('Beschreibung (de)', x["beschreibung_de"], key=f'beschreibung-de-{x["_id"]}')
                    beschreibung_en=st.text_input('Beschreibung (en)', x["beschreibung_en"], key=f'beschreibung-en-{x["_id"]}')
                    kommentar=st.text_area('Kommentar', x["kommentar"])
                    x_updated = {"hp_sichtbar": hp_sichtbar, "name": name, "beschreibung_de": beschreibung_de, "beschreibung_en": beschreibung_en, "kommentar": kommentar}
                    submit = st.form_submit_button('Speichern', type = 'primary')
                    if submit:
                        tools.update_confirm(collection, x, x_updated, )
                        time.sleep(2)
                        st.session_state.edit = ""
                        st.rerun()                      

else:
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
