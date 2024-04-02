import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import datetime 
import pymongo
import pandas as pd
from itertools import chain

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
def edit(id, ex = "termine"):
    st.session_state.page = "Veranstaltung"
    st.session_state.expanded = ex
    st.session_state.edit = id

def update_verwendbarkeit(id, mod_list, an_list, verwendbarkeit):
    veranstaltung.update_one({"_id": id}, { "$set" : { "verwendbarkeit_modul": mod_list, "verwendbarkeit_anforderung": an_list, "verwendbarkeit": verwendbarkeit }})

semesters = list(semester.find(sort=[("kurzname", pymongo.DESCENDING)]))

# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    #st.write(f"edit: {st.session_state.edit}")
    if st.session_state.edit == "" or st.session_state.page != "Veranstaltung":
        #st.write(st.session_state.expanded)
        #st.write(st.session_state.page)
        st.header("Veranstaltungen")
        sem_id = st.selectbox(label="Semester", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester), format_func = (lambda a: semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed")
        st.session_state.semester = sem_id
        if sem_id is not None:
            kat = list(kategorie.find({"semester": sem_id}, sort=[("rang", pymongo.ASCENDING)]))
            submit = False
            for k in kat:
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
                        s = f"{v['name_de']} ({', '.join(d) if d else ''})"
                        st.button(s, key=f"edit-{v['_id']}", on_click = edit, args = (v["_id"], ))
    else:
        x = veranstaltung.find_one({"_id": st.session_state.edit})
        st.session_state.semester = x["semester"]
        col1, col2 = st.columns([1,1])
            
        st.subheader(repr(collection, x["_id"]))

        col1, col2 = st.columns([1,1])
        with col1:
            with st.popover('Veranstaltung löschen'):
                s = ("  \n".join(tools.find_dependent_items(collection, x["_id"])))
                if s:
                    st.write("Eintrag wirklich löschen?  \n" + s + "  \nwerden dadurch geändert.")
                else:
                    st.write("Eintrag wirklich löschen?  \nEs gibt keine abhängigen Items.")
                colu1, colu2, colu3 = st.columns([1,1,1])
                with colu1:
                    st.button(label = "Ja", type = 'primary', on_click = tools.delete_item_update_dependent_items, args = (collection, x["_id"]), key = f"delete-{x['_id']}")
                with colu3: 
                    st.button(label="Nein", on_click = reset, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
        with col2:
            with st.popover('Veranstaltung kopieren'):
                st.write("Kopiere " + repr(collection, x["_id"]))
                st.write("In welches Semester soll kopiert werden?")
                sem_ids = [x["_id"] for x in semesters]
                kop_sem_id = st.selectbox(label="In welches Semester kopieren?", options = sem_ids, index = sem_ids.index(st.session_state.semester), format_func = (lambda a: semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = f"kopiere_veranstaltung_{x['_id']}_sem")
                if kop_sem_id != st.session_state.semester:
                    st.write("Kategorie und Code können nicht kopiert werden, da sie semesterabhängig sind. URL wird nicht kopiert.")
                st.write("Was soll mitkopiert werden?")
                kopiere_personen = st.checkbox("Personen", value = True, key = f"kopiere_veranstaltung_{x['_id']}_per")
                kopiere_termine = st.checkbox("Termine/Räume", value = False, key = f"kopiere_veranstaltung_{x['_id']}_ter")
                kopiere_kommVVZ = st.checkbox("Kommentariertes VVZ", value = True, key = f"kopiere_veranstaltung_{x['_id']}_komm")
                kopiere_verwendbarkeit = st.checkbox("Verwendbarkeit", value = True, key = f"kopiere_veranstaltung_{x['_id']}_ver")
                colu1, colu2 = st.columns([1,1])
                with colu1:
                    st.button(label = "Kopieren", type = 'primary', on_click = tools.kopiere_veranstaltung, args = (x["_id"], kop_sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit), key = f"copy-{x['_id']}")
                with colu2: 
                    st.button(label="Abbrechen", on_click = reset, args=("Nicht kopiert!",), key = f"not-copied-{x['_id']}")

        with st.expander("Grunddaten", expanded = True if st.session_state.expanded == "grunddaten" else False):
            with st.form(f'Grunddaten-{x["_id"]}'):
                hp_sichtbar = st.checkbox("Auf Homepages sichtbar", x["hp_sichtbar"])
                name_de=st.text_input('Name (de)', x["name_de"])
                name_en=st.text_input('Name (en)', x["name_en"])
                midname_de=st.text_input('Mittelkurzer Name (de)', x["midname_de"])
                midname_en=st.text_input('Mittelkurzer Name (en)', x["midname_en"])
                kurzname=st.text_input('Kurzname', x["kurzname"])
                ects=st.text_input('ECTS', x["ects"])
                kat = [g["_id"] for g in list(kategorie.find({"semester": x["semester"]}))]
                index = [g for g in kat].index(x["kategorie"])
                kategorie = st.selectbox("Kategorie", [x for x in kat], index = index, format_func = (lambda a: repr(kategorie, a)))
                cod = st.multiselect("Codes", [x["_id"] for x in code.find({"$or": [{"semester": st.session_state.semester}, {"_id": {"$in": x["code"]}}]}, sort = [("rang", pymongo.ASCENDING)])], x["code"], format_func = (lambda a: repr(code, a)), placeholder = "Bitte auswählen")
                # Sortiere codes nach ihrem Rang 
                cod = [x["_id"] for x in code.find({"$or": [{"semester": st.session_state.semester}, {"_id": {"$in": cod}}]}, sort = [("rang", pymongo.ASCENDING)])]
                kommentar_html_de = st.text_area('Kommentar (HTML, de)', x["kommentar_html_de"])
                kommentar_html_en = st.text_area('Kommentar (HTML, en)', x["kommentar_html_en"])
                url=st.text_input('URL', x["url"])
                ver_updated = {
                    "hp_sichtbar": hp_sichtbar,
                    "name_de": name_de,
                    "name_en": name_en,
                    "midname_de": midname_de,
                    "midname_en": midname_en,
                    "kurzname": kurzname,
                    "ects": ects,
                    "kategorie": kategorie,
                    "code": code,
                    "url": url,
                    "kommentar_html_de": kommentar_html_de,
                    "kommentar_html_en": kommentar_html_en
                }
                submit = st.form_submit_button('Speichern', type = 'primary')
                if submit:
                    st.session_state.expanded = "grunddaten"
                    tools.update_confirm(collection, x, ver_updated, reset = False)

        with st.expander("Personen, Termine etc", expanded = True if st.session_state.expanded == "termine" else False):
            ## Personen, dh Dozent*innen, Assistent*innen und weitere Organisation
            st.subheader("Personen")
            pe = list(person.find({"$or": [{"sichtbar": True, "semester": { "$elemMatch": { "$eq": x["semester"]}}}, {"veranstaltung": { "$elemMatch": { "$eq": x["_id"]}}}]}, sort = [("rang", pymongo.ASCENDING)]))
            per_dict = {p["_id"]: repr(person, p["_id"], show_collection = False) for p in pe }

            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                doz_list = st.multiselect("Dozent*innen", per_dict.keys(), x["dozent"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen")
            with col2: 
                ass_list = st.multiselect("Assistent*innen", per_dict.keys(), x["assistent"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen")
            with col3: 
                org_list = st.multiselect("Organisation", per_dict.keys(), x["organisation"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen")

            pe = list(person.find({"sichtbar": True, "semester": { "$elemMatch": { "$eq": x["semester"]}}}, sort = [("rang", pymongo.ASCENDING)]))

            st.subheader("Wöchentliche Termine")
            wt = x["woechentlicher_termin"]
            woechentlicher_termin = []
            for i, w in enumerate(wt):
                cols = st.columns([1,1,5,5,5,5,5,5,1])
                with cols[0]:
                    st.write("")
                    st.write("")
                    st.button('↓', key=f'down-w-{i}', on_click = tools.move_down_list, args = (collection, x["_id"], "woechentlicher_termin", w,))
                with cols[1]:
                    st.write("")
                    st.write("")
                    st.button('↑', key=f'up-w-{i}', on_click = tools.move_up_list, args = (collection, x["_id"], "woechentlicher_termin", w,))
                with cols[2]:
                    w_key = (st.text_input("Art des Termins", w["key"], key = f"termin_{i}_art"))
                with cols[3]:
                    termin_raum = list(raum.find({"$or": [{"sichtbar": True}, {"_id": w["raum"]}]}, sort = [("rang", pymongo.ASCENDING)]))
                    termin_raum_dict = {r["_id"]: repr(raum, r["_id"], show_collection = False) for r in    termin_raum }
                    index = [g["_id"] for g in termin_raum].index(w["raum"])
                    w_raum = st.selectbox("Raum", termin_raum_dict.keys(), index, format_func = (lambda a: termin_raum_dict[a]), key = f"termin_{i}_raum")
#                termin_raum_person_list = st.multiselect("Personen", per_dict.keys(), w["person"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen")
                def wochentag_zeit_option(wochentag, time):
                    pass
                with cols[4]:
                    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
                    try:
                        wochentag_index = wochentage.index(w["wochentag"])
                    except:
                        wochentag_index = None
                    w_wochentag = st.selectbox("Tag", wochentage, wochentag_index, key = f"termin_{i}_wochentag", placeholder = "Bitte auswählen")
                with cols[5]:
                    w_start = st.time_input("Start", w["start"], key =f"termin_{i}_start")
                with cols[6]:
                    w_ende = st.time_input("Ende", w["ende"], key =f"termin_{i}_ende")
                with cols[7]:
                    w_kommentar = st.text_input("Kommentar", w["kommentar"], key =f"termin_{i}_kommentar")
                with cols[8]:
                    st.write("")
                    st.write("")
                    st.button('✕', key=f'close-w-{i}', on_click = tools.remove_from_list, args = (collection, x["_id"], "woechentlicher_termin", w,))
                woechentlicher_termin.append({
                    "key": w_key,
                    "raum": w_raum,
                    "person": [],
                    "wochentag": w_wochentag,                    
                    "start": None if w_start == None else datetime.datetime.combine(datetime.datetime(1970,1,1), w_start),
                    "ende": None if w_ende == None else datetime.datetime.combine(datetime.datetime(1970,1,1), w_ende),
                    "kommentar": w_kommentar
                })
            ver_updated = {
                "dozent": doz_list,
                "assistent": ass_list,
                "organisation": org_list,
                "woechentlicher_termin": woechentlicher_termin
            }
            neuer_termin = st.button('Neuer Termin')
            submit = st.button('Speichern', type = 'primary')
            if neuer_termin or submit:
                st.session_state.expanded = "termin"
                tools.update_confirm(collection, x, ver_updated, reset = False)
            if neuer_termin:
                leerer_termin = {
                    "key": "",
                    "kommentar": "",
                    "wochentag": None,
                    "raum": raum.find_one({"name_de": "-"})["_id"],
                    "person": [person.find_one({"name": "-"})["_id"]],
                    "start": None,
                    "ende": None
                }
                veranstaltung.update_one({"_id": x["_id"]}, { "$push": {"woechentlicher_termin": leerer_termin}})
                st.rerun()
        with st.expander("Kommentiertes Vorlesungsverzeichnis", expanded = True if st.session_state.expanded == "kommentiertes_VVZ" else False):
            with st.form(f'Kommentiertes-VVZ-{x["_id"]}'):
                inhalt_de = st.text_area('Inhalt (de)', x["inhalt_de"])
                inhalt_en = st.text_area('Inhalt (en)', x["inhalt_en"])
                literatur_de = st.text_area('Literatur (de)', x["literatur_de"])
                literatur_en = st.text_area('Literatur (en)', x["literatur_en"])
                vorkenntnisse_de = st.text_area('Vorkenntnisse (de)', x["vorkenntnisse_de"])
                vorkenntnisse_en = st.text_area('Vorkenntnisse (en)', x["vorkenntnisse_en"])
                kommentar_latex_de = st.text_area('Kommentar (Latex, de)', x["kommentar_latex_de"])
                kommentar_latex_en = st.text_area('Kommentar (Latex, en)', x["kommentar_latex_en"])
                ver_updated = {
                    "inhalt_de": inhalt_de,
                    "inhalt_en": inhalt_en,
                    "literatur_de": literatur_de,
                    "literatur_en": literatur_en,
                    "vorkenntnisse_de": vorkenntnisse_de,
                    "vorkenntnisse_en": vorkenntnisse_en,
                    "kommentar_latex_de": kommentar_latex_de,
                    "kommentar_latex_en": kommentar_latex_en
                }
                submit = st.form_submit_button('Speichern', type = 'primary')
                if submit:
                    st.session_state.expanded = "kommentiertes_VVZ"
                    tools.update_confirm(collection, x, ver_updated, reset = False)

        ## Verwendbarkeiten
        with st.expander("Verwendbarkeit", expanded = True if st.session_state.expanded == "verwendbarkeit" else False):
            st.subheader("Verwendbarkeit")
            with st.popover("Aus anderer Veranstaltung importieren"):
                ver_auswahl = list(veranstaltung.find({"$or": [{"kategorie": x["kategorie"]}, {"dozent": {"$in": x["dozent"]}}]}))
                verwendbarkeit_import = st.selectbox("Veranstaltung", [v["_id"] for v in ver_auswahl], format_func = (lambda a: repr(veranstaltung, a, show_collection=False)))
                v = veranstaltung.find_one({"_id": verwendbarkeit_import})
                x_updated = {"verwendbarkeit_modul": v["verwendbarkeit_modul"],
                             "verwendbarkeit_anforderung": v["verwendbarkeit_anforderung"],
                             "verwendbarkeit": v["verwendbarkeit"]}
                colu1, colu2 = st.columns([1,1])
                with colu1:
                    st.button(label = "Importieren", type = 'primary', on_click = tools.update_confirm, args = (veranstaltung, x, x_updated, False), key = f"import-verwendbarkeit-{x['_id']}")
                with colu2: 
                    st.button(label="Abbrechen", on_click = reset, args=("Nicht kopiert!",), key = f"not-imported-{x['_id']}")

            mo = list(modul.find({"$or": [{"sichtbar": True}, {"_id": { "$elemMatch": { "$eq": x["verwendbarkeit_modul"]}}}]}, sort = [("rang", pymongo.ASCENDING)]))
            mo_dict = {m["_id"]: repr(modul, m["_id"], show_collection = False) for m in mo }
            mod_list = st.multiselect("Module", mo_dict.keys(), x["verwendbarkeit_modul"], format_func = (lambda a: mo_dict[a]), placeholder = "Bitte auswählen")

            ver_an = list(anforderung.find({"$or": [{"sichtbar": True}, {"_id": { "$elemMatch": { "$eq": x["verwendbarkeit_anforderung"]}}}]}, sort = [("rang", pymongo.ASCENDING)]))
            an_dict = {a["_id"]: repr(anforderung, a["_id"], show_collection = False) for a in ver_an }
            an_list = st.multiselect("Anforderung", an_dict.keys(), x["verwendbarkeit_anforderung"], format_func = (lambda a: an_dict[a]), placeholder = "Bitte auswählen")

            data = {m : [] for m in mod_list}
            g = pd.DataFrame(data)
            cols = st.columns([15] + [15/len(mod_list) for x in mod_list])
            for i, m in enumerate(mod_list):
                with cols[i+1]:
                    co1, co2 = st.columns([1,1])
                    with co1:
                        st.button('←', key=f'left-m-{m}', on_click = tools.move_up_list, args = (collection, x["_id"], "verwendbarkeit_modul", m,))
                    with co2:
                        st.button('→', key=f'right-m-{m}', on_click = tools.move_down_list, args = (collection, x["_id"], "verwendbarkeit_modul", m,))
                    st.write(mo_dict[m])
            for a in an_list:
                cols = st.columns([1,1,13] + [15/len(mod_list) for x in mod_list])
                with cols[0]:
                    st.button('↓', key=f'down-a-{a}', on_click = tools.move_down_list, args = (collection, x["_id"], "verwendbarkeit_anforderung", a,))
                with cols[1]:
                    st.button('↑', key=f'up-a-{a}', on_click = tools.move_up_list, args = (collection, x["_id"], "verwendbarkeit_anforderung", a,))
                with cols[2]:
                    st.write(an_dict[a])
                for i, m in enumerate(mod_list):
                    with cols[i+3]:
                        g.loc[a,m] = st.checkbox("",True if { "modul": m, "anforderung": a } in x["verwendbarkeit"] else False, key = f"anforderung_{a}_modul_{m}")
            verwendbarkeit = [{"modul": m, "anforderung": a} for m in mod_list for a in an_list if g.loc[a,m] == True]
            x_updated = { "verwendbarkeit_modul": mod_list, "verwendbarkeit_anforderung": an_list, "verwendbarkeit": verwendbarkeit }
            submit = st.button('Speichern', type = 'primary', on_click = tools.update_confirm, args = (veranstaltung, x, x_updated, False,), key = f"verwendbarkeit_{x['_id']}")

    # st.rerun()

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
