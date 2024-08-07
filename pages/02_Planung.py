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
collection = util.planung
catcollection = util.planungkategorie

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
    if semname[5:6] == "WS":
        res = f"{int(semname[0:4])+1}SS"
    else:
        res = f"{int(semname[0:4])}WS"
    return res

def sembetween(startsemester, endsemester):
    startyear = int(startsemester[0:4])
    startwsss = startsemester[5:6]
    endwsss = endsemester[5:6]
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

semesters = semlist(2000,2100)

collection = util.semester
# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Planung künftiger Semester")

  # Auswahl von Semester
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.write("Anzeige von...")
        semester_start = st.selectbox(label="von", options = semesters, index = semesters.index(tools.get_semester_in_years(0)), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_von")
    with col2:
        st.write("...bis...")
        semester_end = st.selectbox(label="von", options = semesters, index = semesters.index(tools.get_semester_in_years(5)), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_bis")
    semester_auswahl = sembetween(semester_start, semester_end)
    st.write(semester_auswahl)
    st.divider()
    catlist = list(catcollection.find(sort=[("rang", pymongo.ASCENDING)]))
    cols = st.columns([1, 1, 1, 10] + [15/len(semester_auswahl) for x in semester_auswahl])
    for i, m in enumerate(semester_auswahl):
        with cols[i+4]:
            st.write(m)

    for c in catlist:
        cols[3].write(c["name"])
        planunglist = list(collection.find({"kategorie" : c["_id"]}, sort=[("rang", pymongo.ASCENDING)]))





else:
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
