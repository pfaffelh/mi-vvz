import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
import pandas as pd
from bson import ObjectId


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
collection_ver = util.statistikveranstaltung
collection_sem = util.statistiksemester

if st.session_state.page != "Statistik":
    st.session_state.edit = ""
st.session_state.page = "Statistik"

def kurzname_of_id(id):
    try:
        x = util.semester.find_one({"_id": id})["kurzname"]
    except:
        x = util.studiengang.find_one({"_id": id})["kurzname"]        
    return x

def id_of_kurzname(kurzname):
    x = util.semester.find_one({"kurzname": kurzname})["_id"]
    return x

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Statistiken")
    st.write("Es gibt Statistiken von Semestern (z.B. Einschreibestatistiken) und Statistiken von Veranstaltungen (z.B. Belegzahlen).")
    st.write(" ")
    st.write("### Semesterstatistiken")
    with st.expander(f'Neue Statistik anlegen'):
        st.write("Neu")

    stat = list(util.statistiksemester.find({}, sort = [("rang", pymongo.ASCENDING)]))
    for s in stat:
        with st.expander(s["name"]):
            name=st.text_input('Name', s["name"], key = f"name_{s['_id']}")
            semester_list = st.multiselect("Semester", [x["_id"] for x in util.semester.find(sort = [("kurzname", pymongo.DESCENDING)])], s["semester"], format_func = (lambda a: tools.repr(util.semester, a, False, True)), placeholder = "Bitte auswählen", key = f"semester_{s['_id']}")
            st.write(semester_list)
            se = list(util.semester.find({"_id": {"$in": semester_list}}, sort=[("rang", pymongo.ASCENDING)]))
            semester_list = [s["_id"] for s in se]
            stu_list = st.multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"$or": [{"sichtbar": True}, {"_id": {"$in": s["studiengang"]}}]}, sort = [("name", pymongo.ASCENDING)])], s["studiengang"], format_func = (lambda a: tools.repr(util.studiengang, a, False)), placeholder = "Bitte auswählen", key = f"studiengang_{s['_id']}")
            stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
            stu_list = [str(s["_id"]) for s in stu]

            kommentar=st.text_input('Kommentar', s["kommentar"], key = f"kommentar_{s['_id']}")

            if stu_list != []:
                stat = [{ "semester" : kurzname_of_id(x["semester"]), "studiengang" : str(x["studiengang"]), "wert" : x["wert"]} for x in s["stat"] if str(x["studiengang"]) in stu_list and x["semester"] in semester_list]
                for se in semester_list:
                    for stu in stu_list:
                        if len([item for item in stat if item["semester"] == kurzname_of_id(se) and item["studiengang"] == stu]) == 0:
                            stat.append({"semester" : kurzname_of_id(se), "studiengang": stu, "wert" : 0})
                df = pd.DataFrame.from_records(stat)
                crosstab = pd.crosstab(df["semester"], df["studiengang"], values = df["wert"], aggfunc = 'sum') 
                edited_crosstab = st.data_editor(crosstab, column_config = { stu : kurzname_of_id(ObjectId(stu)) for stu in stu_list}, key = f"df_{s['_id']}")
                stat = []
                for row in edited_crosstab.index:
                    for col in edited_crosstab.columns:
                        stat.append({"semester" : id_of_kurzname(row), "studiengang" : ObjectId(col), "wert": int(edited_crosstab.loc[row, col])})   
            else:
                stat = [{ "semester" : kurzname_of_id(x["semester"]), "wert" : x["wert"]} for x in s["stat"]]
                for se in semester_list:
                    if len([item for item in stat if item["semester"] == kurzname_of_id(se)]) == 0:
                        stat.append({"semester" : se, "wert" : 0})
                df = pd.DataFrame.from_records(stat)
                df = st.data_editor(df, key = f"df_{s['_id']}")
                stat = df.to_dict('records')

            s_updated = ({"name": name, "semester": semester_list, "studiengang": [ObjectId(s) for s in stu_list], "stat": stat, "kommentar": kommentar})

            submit = st.button('Speichern', type = 'primary', key = f"submit_{s['_id']}")
            if submit:
                tools.update_confirm(collection_sem, s, s_updated, )
                time.sleep(.1)
        
            
            
    st.write("### Veranstaltungsstatistiken")
    with st.expander(f'Neue Statistik anlegen'):
        st.write("")
        
        
        
        



else:
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
