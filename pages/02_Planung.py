import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
import pandas as pd
from datetime import datetime

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
planung = util.planung
veranstaltung = util.planungveranstaltung

# Für die Auswahl der Einträge einer neuen Planung
def semlist(startyear, endyear):
    res = []
    i = startyear
    while i <= endyear:
        res.append(f"{i}SS")
        res.append(f"{i}WS")
        i = i+1
    return res

def nextsemester(semname):
    if semname[4:6] == "WS":
        res = f"{int(semname[0:4])+1}SS"
    else:
        res = f"{int(semname[0:4])}WS"
    return res

def sembetween(startsemester, endsemester):
    startyear = int(startsemester[0:4])
    startwsss = startsemester[4:6]
    endwsss = endsemester[4:6]
    endyear = int(endsemester[0:4])
    if startyear > endyear or (startyear == endyear and startwsss == "WS" and endwsss == "SS"):
        res = []
    else:
        res = [startsemester]
        loc = startsemester
        while loc != endsemester:
            loc = nextsemester(loc)
            res.append(loc)
    return res

def is_WS(semester):
    return semester[4:6] == "WS"

# Nur Nachname einer Person
def nachname(id):
    x = util.person.find_one({"_id": id})
    return f"{x['name']}"

#last_sem = util.semester.find_one(sort = [("name", pymongo.ASCENDING)])
#last_sem_id = last_sem["_id"]
#dozlist = []
#for v in util.veranstaltung.find({"semester" : last_sem["_id"]}):
#    dozlist = dozlist + v["dozent"]
#dozlist = list(set(dozlist))
#per_dict = {p: tools.repr(util.person, p, False, True) for p in dozlist }
pe = list(util.person.find({"semester": { "$elemMatch": {"$eq": st.session_state.semester_id}}}, sort=[("name", pymongo.ASCENDING), ("vorname", pymongo.ASCENDING)]))
per_dict = {p["_id"]: tools.repr(util.person, p["_id"], False, True) for p in pe }

semesters = semlist(2010,2050)
name = {}
dozent = {}
sem = {}
kommentar = {}                
sws = {}
regel = {}

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Planung künftiger Semester")

  # Auswahl von Semester
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.write("Anzeige von...")
        semester_start = st.selectbox(label="von", options = semesters, index = semesters.index(tools.get_semester_in_years(1)), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_von")
    with col2:
        st.write("...bis...")
        semester_end = st.selectbox(label="von", options = semesters, index = semesters.index(tools.get_semester_in_years(4)), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_bis")
    semester_auswahl = sembetween(semester_start, semester_end)
    st.divider()
    
    col_list = [1, 1, 1, 5] + [15/len(semester_auswahl) for x in semester_auswahl]
    cols = st.columns(col_list)
    for i, m in enumerate(semester_auswahl):
        with cols[i+4]:
            header = st.container()
            header.write(m)
    
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

    ### Custom CSS for the sticky header
    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2.875rem;
            background-color: white;
            z-index: 999;
        }
        .fixed-header {
            border-bottom: 1px solid black;
        }
    </style>
        """,
        unsafe_allow_html=True
    )
    
    verlist = list(veranstaltung.find(sort=[("rang", pymongo.ASCENDING)]))
    col_list = [1, 1, 1, 5] + [15/len(semester_auswahl) for x in semester_auswahl]
    cols = st.columns(col_list)
    with cols[3]:
        with st.popover("Neue Veranstaltung"):
            with st.form("Veranstaltung anlegen", clear_on_submit=True):
                name["new"] = st.text_input("Name", key = "name_v_neu")
                sws["new"] = st.text_input("SWS", key = "sws_v_neu")
                regel["new"] = st.selectbox("Regelmäßigkeit", ("Jedes Wintersemester", "Jedes Sommersemester", "Jedes Semester"), key = "regel_v_neu")
                kommentar["new"] = st.text_input("Kommentar", key = "kommentar_v_neu")
                st.form_submit_button("Veranstaltung anlegen", on_click = tools.new, args = (util.planungveranstaltung, {"name": name["new"], "sws": sws["new"], "regel": regel["new"], "kommentar": kommentar["new"]}, False,))
#    for i, m in enumerate(semester_auswahl):
#        with cols[i+4]:
#            st.write(m)

    for v in verlist:
        cols = st.columns(col_list)
        with cols[0]:
            st.button('↓', key=f'down-{v["_id"]}', on_click = tools.move_down, args = (util.planungveranstaltung, v, ))
        with cols[1]:
            st.button('↑', key=f'up-{v["_id"]}', on_click = tools.move_up, args = (util.planungveranstaltung, v, ))
        with cols[2]:
            with st.popover('🗙', use_container_width=True):
                colu1, colu2 = st.columns([1,1])
                with colu1:
                    st.button(label = "Wirklich löschen!", type = 'primary', on_click = tools.delete_item_update_dependent_items, args = (util.planungveranstaltung, v["_id"], False), key = f"delete-{v['_id']}")
                with colu2: 
                    st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{v['_id']}")
        with cols[3]:
            with st.popover(v["name"]):
                name[v['_id']] = st.text_input("Name", v["name"], key = f"name_{v['_id']}")
                sws[v['_id']] = st.text_input("SWS", v["sws"], key = f"sws_{v['_id']}")
                regel[v['_id']] = st.selectbox("Regelmäßigkeit", ("Jedes Wintersemester", "Jedes Sommersemester", "Jedes Semester"), ("Jedes Wintersemester", "Jedes Sommersemester", "Jedes Semester").index(v["regel"]), key = f"regel_{v['_id']}")
                kommentar[v['_id']] = st.text_input("Kommentar", v["kommentar"], key = f"kommentar_{v['_id']}")
                x_updated = {"name": name[v['_id']], "sws": sws[v['_id']], "regel": regel[v['_id']], "kommentar": kommentar[v['_id']]}
                st.button("Speichern", on_click=tools.update_confirm, args = (util.planungveranstaltung, v, x_updated, False,), key = f"save_{v['_id']}")
        for i, m in enumerate(semester_auswahl):
            with cols[i+4]:
                p = planung.find_one({"veranstaltung": v["_id"], "sem": m})
                if v["regel"] == "Jedes Semester" or (is_WS(m) and v["regel"] == "Jedes Wintersemester") or (not is_WS(m) and v["regel"] == "Jedes Sommersemester"):
                    if p:
                        with st.popover(", ".join([nachname(q) for q in p["dozent"]]), use_container_width=True):
                            dozent[p['_id']] = st.multiselect("Dozent*innen", per_dict.keys(), p["dozent"], format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen", key = f"dozent_{p['_id']}")
                            sem[p['_id']] = st.selectbox("Semester", options = semesters, index = semesters.index(m), key = f"sem_{p['_id']}")
                            kommentar[p['_id']] = st.text_input("Kommentar", p["kommentar"], key = f"kommentar_{p['_id']}")
                            colu1, colu2 = st.columns([1,1])
                            with colu1:
                                st.button("Speichern", on_click = tools.update_confirm, args = (util.planung, p, {"dozent": dozent[p['_id']], "sem": sem[p['_id']], "kommentar": kommentar[p['_id']]}, False,), key = f"save_{p['_id']}")
                            with colu2:
                                st.button("Löschen", on_click=tools.delete_item_update_dependent_items, args = (util.planung, p["_id"], False,), key = f"delete_{p['_id']}")
                             
                    else:
                        with st.popover("➕", use_container_width=True):
                            dozent[f"{v['_id']}_{m}"] = st.multiselect("Dozent*innen", per_dict.keys(), format_func = (lambda a: per_dict[a]), placeholder = "Bitte auswählen", key = f"dozent_{v['_id']}_{m}")
                            sem[f"{v['_id']}_{m}"] = st.selectbox("Semester", options = semesters, index = semesters.index(m), key = f"sem_{v['_id']}_{m}")
                            kommentar[f"{v['_id']}_{m}"] = st.text_input("Kommentar", key = f"kommentar_{v['_id']}_{m}")
                            st.button("Speichern", on_click = tools.new, args = (util.planung, {"veranstaltung": v["_id"], "dozent": dozent[f"{v['_id']}_{m}"], "sem": sem[f"{v['_id']}_{m}"], "kommentar": kommentar[f"{v['_id']}_{m}"]}, False,), key = f"save_{v['_id']}_{m}")
                else:
                    if p:
                        st.write(", ".join([tools.repr(util.person, q, False, True) for q in p["dozent"]]))

else:
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
