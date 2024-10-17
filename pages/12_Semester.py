import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
import pandas as pd

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

    col1, col2 = st.columns([1,1])
    with col1:
        st.write("Hier zurück ohne speichern Button")
    with col2:
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
    with st.expander(f'Neues Semester anlegen'):
        s = list(util.semester.find({}, sort = [("rang", pymongo.DESCENDING)]))
        d = tools.new_semester_dict()
        new_name_de = st.text_input('Name des angelegten Semesters (de)', d["name_de"], disabled = True)
        new_name_en = st.text_input('Name des angelegten Semesters (en)', d["name_en"], disabled = True)
        new_kurzname = st.text_input('Kurzname des angelegten Semesters', d["kurzname"], disabled = True)
        new_hp_sichtbar = st.checkbox(f"Auf Homepage sichtbar", value = False, key=f'kopie-hp_sichtbar')
        personen_uebernehmen = st.checkbox(f"Personen aus {s[0]['name_de']} in die Personenliste des Semesters übernehmen", value = True, key=f'personen_uebernehmen')
        anforderung_uebernehmen = st.checkbox(f"Anforderungen aus {s[0]['name_de']} übernehmen", value = True, key=f'anforderung_uebernehmen')
        veranstaltungen_uebernehmen = st.checkbox(f"Veranstaltungen aus {s[1]['name_de']} übernehmen. (Rubriken und Codes von Veranstaltungen werden übernommen, Anforderungen auch, URLs nicht.)", value = True, key=f'veranstaltungen_uebernehmen')
        last_sem_kurzname = list(util.semester.find(sort = [("rang", pymongo.DESCENDING)]))[0]["kurzname"]
        x_updated = {"name_de": new_name_de, 
                     "name_en": new_name_en, 
                     "kurzname": new_kurzname, 
                     "hp_sichtbar": new_hp_sichtbar, 
                     "rubrik": [], 
                     "code": [], 
                     "prefix_de": "", 
                     "prefix_en": "", 
                     "vorspann_kommentare_de": "", 
                     "vorspann_kommentare_en": "", 
                     "veranstaltung": [], 
                     "rang": s[0]["rang"]+1
                     }
        rub_list = list(util.rubrik.find({"semester": s[1]["_id"]}, sort = [("rang", pymongo.ASCENDING)]))
        ver_list = []
        for r in rub_list:
            ver_list.extend([v["_id"] for v in list(util.veranstaltung.find({"rubrik": r["_id"]}, sort = [("rang", pymongo.ASCENDING)]))])
        g = [{"_id": v, "Name": tools.repr(util.veranstaltung, v, False), "Veranstaltung übernehmen": veranstaltungen_uebernehmen, "...mit Dozenten/Assistenten": False, "...mit Terminen": False, "...mit Kommentaren": False, "...mit Verwendbarkeit": True} for v in ver_list]
        df = df_new = pd.DataFrame.from_records(g)
        if veranstaltungen_uebernehmen:
            df_new = st.data_editor(
                df, height = None, column_config = {"_id": None}, disabled=["Name"], hide_index = True)
        st.button("Semester anlegen", on_click=tools.semester_anlegen, args = (x_updated, df_new, personen_uebernehmen, anforderung_uebernehmen, veranstaltungen_uebernehmen), type="primary")
    with st.form(f'ID-{x["_id"]}'):
        name_de = st.text_input('Name (de)', x["name_de"], disabled = True)
        name_en = st.text_input('Name (en)', x["name_en"], disabled = True)
        kurzname = st.text_input('Kurzname', x["kurzname"], disabled = True)
        hp_sichtbar = st.checkbox(f"Auf www.math... sichtbar {'😎' if x['hp_sichtbar'] else ''}", value = x["hp_sichtbar"], key=f'ID-{x["_id"]}-hp_sichtbar')
        prefix_de = st.text_area('Prefix (de)', x["prefix_de"], help="Dieser Text erscheint oben auf der Veranstaltungsseite des Semesters.")
        prefix_en = st.text_area('Prefix (en)', x["prefix_en"], help="Dieser Text erscheint oben auf der Veranstaltungsseite des Semesters.")
        x_updated = {"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "hp_sichtbar": hp_sichtbar, "prefix_de": prefix_de, "prefix_en": prefix_en}
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
    query = { "semester": st.session_state.semester_id }
    y = list(collection.find(query, sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, query,))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, query,))
        with co3:
            abk = x['titel_de'].replace(".", ":")
            abk = f"{abk} 😎" if x["hp_sichtbar"] else f"{abk}"
            with st.expander(abk, (True if x["_id"] == st.session_state.edit else False)):
                with st.popover('Rubrik löschen'):
                    s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
                    if s:
                        st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
                    else:
                        st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        if x["titel_de"] != "-":
                            submit = st.button(label = "Ja", type = 'primary', key = f"delete-{x['_id']}")
                        else:
                            submit = st.button(label = "Ja", type = 'primary', disabled = True, key = f"delete-{x['_id']}", help = "Diese Rubrik wird beim Kopieren von Veranstaltungen benötigt und kann daher nicht gelöscht werden.")
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
                    suffix_de=st.text_area('Suffix (de)', x["suffix_de"], key=f'suffix-de-{x["_id"]}')
                    suffix_en=st.text_area('Suffix (en)', x["suffix_en"], key=f'suffix-en-{x["_id"]}')
                    kommentar=st.text_area('Kommentar', x["kommentar"])
                    x_updated = {"hp_sichtbar": hp_sichtbar, "titel_de": titel_de, "titel_en": titel_en, "untertitel_de": untertitel_de, "untertitel_en": untertitel_en, "prefix_de": prefix_de, "prefix_en": prefix_en, "suffix_de": suffix_de, "suffix_en": suffix_en, "kommentar": kommentar}
                    submit = st.form_submit_button('Speichern', type = 'primary')
                    if submit:
                        tools.update_confirm(collection, x, x_updated, )
                        time.sleep(2)
                        st.session_state.edit = ""
                        st.rerun()                      

    st.write("### Kategorie von Codes")
    st.write('Dies ist z.B. "Sprache". Dann kann in den Codes dieser Codekategorie so etwas stehen wie "Vorlesung in englischer Sprache". Ein anderes Beispiel ist eine Codekategorie "Evaluation". Hier könnte eine Code angeben, ob die entsprechende Veranstaltung evaluiert werden soll.' )
    collection = util.codekategorie
    st.write(" ")
    if st.button('**Neue Codekategorie hinzufügen**'):
        tools.new(collection, ini = { "semester": st.session_state.semester_id }, switch = False)

    query = { "semester": st.session_state.semester_id }
    y = list(collection.find(query, sort=[("rang", pymongo.ASCENDING)]))

    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, query, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, query, ))
        with co3:   
            abk = f"{x['name_de'].strip()}"
            abk = f"{abk.strip()} 😎" if x["hp_sichtbar"] else f"{abk.strip()}"
            with st.expander(abk, (True if x["_id"] == st.session_state.edit else False)):
                with st.popover('Codekategorie löschen'):
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
                    komm_sichtbar = st.checkbox(f"Im kommentierten VVZ sichtbar {'🤓' if x['komm_sichtbar'] else ''}", x["komm_sichtbar"], disabled = False)
                    name_de=st.text_input('Titel (de)', x["name_de"], key=f'titel-de-{x["_id"]}')
                    name_en=st.text_input('Titel (en)', x["name_en"], key=f'titel-en-{x["_id"]}')
                    beschreibung_de=st.text_input('Beschreibung (de)', x["beschreibung_de"], key=f'beschreibung-de-{x["_id"]}')
                    beschreibung_en=st.text_input('Beschreibung (en)', x["beschreibung_en"], key=f'beschreibung-en-{x["_id"]}')
                    kommentar=st.text_area('Kommentar', x["kommentar"])
                    code = []
                    x_updated = {"hp_sichtbar": hp_sichtbar, "komm_sichtbar": komm_sichtbar, "name_de": name_de, "name_en": name_en, "beschreibung_de": beschreibung_de, "kommentar": kommentar, "code": []}
                    submit = st.form_submit_button('Speichern', type = 'primary')
                    if submit:
                        tools.update_confirm(collection, x, x_updated, )
                        time.sleep(2)
                        st.session_state.edit = ""
                        st.rerun()                      

    st.write("### Codes")
    collection = util.code
    if st.button('**Neuen Code hinzufügen**'):
        tools.new(collection, ini = { "semester": st.session_state.semester_id, "codekategorie": util.codekategorie.find_one({"semester": st.session_state.semester_id, "name_de": "Allgemein"})["_id"] }, switch = False)

    query = { "semester": st.session_state.semester_id }
    y = list(collection.find(query, sort=[("rang", pymongo.ASCENDING)]))
    for x in y:
        co1, co2, co3 = st.columns([1,1,23]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, query, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, query, ))
        with co3:   
            abk = f"{x['beschreibung_de'].strip()}, {x['name'].strip()}"
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
                    codekategorie_list = list(util.codekategorie.find({"semester": st.session_state.semester_id}, sort = [("rang", pymongo.ASCENDING)]))
                    codekategorie_dict = {r["_id"]: tools.repr(util.codekategorie, r["_id"], show_collection = False) for r in codekategorie_list}
                    index = [g["_id"] for g in codekategorie_list].index(x["codekategorie"])
                    codekategorie = st.selectbox("Codekategorie", codekategorie_dict.keys(), index, format_func = (lambda a: codekategorie_dict[a]), key = f"codekategorie_{x}")
                    name=st.text_input('Name', x["name"], key=f'name-{x["_id"]}')
                    beschreibung_de=st.text_input('Beschreibung (de)', x["beschreibung_de"], key=f'beschreibung-de-{x["_id"]}')
                    beschreibung_en=st.text_input('Beschreibung (en)', x["beschreibung_en"], key=f'beschreibung-en-{x["_id"]}')
                    kommentar=st.text_area('Kommentar', x["kommentar"])
                    x_updated = {"codekategorie": codekategorie, "name": name, "beschreibung_de": beschreibung_de, "beschreibung_en": beschreibung_en, "kommentar": kommentar}
                    submit = st.form_submit_button('Speichern', type = 'primary')
                    if submit:
                        tools.update_confirm(collection, x, x_updated, )
                        time.sleep(2)
                        st.session_state.edit = ""
                        st.rerun()                      



else:
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
