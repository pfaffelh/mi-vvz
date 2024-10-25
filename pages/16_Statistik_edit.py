import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pandas as pd
import time
import pymongo
from bson import ObjectId

def kurzname_of_id(id):
    try:
        x = util.semester.find_one({"_id": id})["kurzname"]
    except:
        x = util.studiengang.find_one({"_id": id})["kurzname"]        
    return x

def id_of_kurzname(kurzname):
    x = util.semester.find_one({"kurzname": kurzname})["_id"]
    return x


# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

from misc.config import *
import misc.util as util
from misc.util import logger
import misc.tools as tools

tools.delete_temporary()

# load css styles
from misc.css_styles import init_css
init_css()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.statistiksemester

new_entry = False

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Semesterabhängige Statistik")

    # check if entry can be found in database
    if st.session_state.edit == "new":
        new_entry = True
        x = st.session_state.new[collection]
        x["semester"] = [st.session_state.semester_id]
        x["_id"] = "new"

    else:
        x = collection.find_one({"_id": st.session_state.edit})
        st.subheader(tools.repr(collection, x["_id"], False))
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Zurück ohne Speichern"):
            switch_page("Statistik")
    with col2:
        with st.popover('Statistik löschen'):
            if not new_entry:
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
        

    with st.form(f'ID-{x["_id"]}'):
        name=st.text_input('Name', x["name"], key = f"name_{x['_id']}")
        semester_list = st.multiselect("Semester", [x["_id"] for x in util.semester.find(sort = [("kurzname", pymongo.DESCENDING)])], x["semester"], format_func = (lambda a: tools.repr(util.semester, a, False, True)), placeholder = "Bitte auswählen", key = f"semester_{x['_id']}")
        se = list(util.semester.find({"_id": {"$in": semester_list}}, sort=[("rang", pymongo.ASCENDING)]))
        semester_list = [x["_id"] for x in se]
        stu_list = st.multiselect("Studiengänge", [x["_id"] for x in util.studiengang.find({"$or": [{"sichtbar": True}, {"_id": {"$in": x["studiengang"]}}]}, sort = [("name", pymongo.ASCENDING)])], x["studiengang"], format_func = (lambda a: tools.repr(util.studiengang, a, False)), placeholder = "Bitte auswählen", key = f"studiengang_{x['_id']}")
        stu = list(util.studiengang.find({"_id": {"$in": stu_list}}, sort=[("name", pymongo.ASCENDING)]))
        stu_list = [str(x["_id"]) for s in stu]

        kommentar=st.text_input('Kommentar', x["kommentar"], key = f"kommentar_{x['_id']}")

        if stu_list != []:
            stat = [{ "semester" : kurzname_of_id(x["semester"]), "studiengang" : str(x["studiengang"]), "wert" : x["wert"]} for x in x["stat"] if str(x["studiengang"]) in stu_list and x["semester"] in semester_list]
            for se in semester_list:
                for stu in stu_list:
                    if len([item for item in stat if item["semester"] == kurzname_of_id(se) and item["studiengang"] == stu]) == 0:
                        stat.append({"semester" : kurzname_of_id(se), "studiengang": stu, "wert" : 0})
            df = pd.DataFrame.from_records(stat)
            crosstab = pd.crosstab(df["semester"], df["studiengang"], values = df["wert"], aggfunc = 'sum') 
            edited_crosstab = st.data_editor(crosstab, key = f"df_{x['_id']}")
#            edited_crosstab = st.data_editor(crosstab, column_config = { stu : kurzname_of_id(ObjectId(stu)) for stu in stu_list}, key = f"df_{x['_id']}")
            stat = []
            for row in edited_crosstab.index:
                for col in edited_crosstab.columns:
                    stat.append({"semester" : id_of_kurzname(row), "studiengang" : ObjectId(col), "wert": int(edited_crosstab.loc[row, col])})   
        else:
            stat = [{ "semester" : kurzname_of_id(x["semester"]), "wert" : x["wert"]} for x in x["stat"]]
            for se in semester_list:
                if len([item for item in stat if item["semester"] == kurzname_of_id(se)]) == 0:
                    stat.append({"semester" : se, "wert" : 0})
            df = pd.DataFrame.from_records(stat)
            df = st.data_editor(df, key = f"df_{x['_id']}")
            stat = df.to_dict('records')

        s_updated = ({"name": name, "semester": semester_list, "studiengang": [ObjectId(s) for s in stu_list], "stat": stat, "kommentar": kommentar})

        submit = st.form_submit_button('Speichern', type = 'primary', key = f"submit_{x['_id']}")
        if submit:
            tools.update_confirm(collection, s, s_updated, )
            time.sleep(.1)
        
            
            
    st.write("### Veranstaltungsstatistiken")
    with st.expander(f'Neue Statistik anlegen'):
        st.write("")
        
        
        
        if submit:
            if new_entry:
                tools.new(collection, ini = x_updated, switch=False)
            else: 
                tools.update_confirm(collection, x, x_updated, )
            time.sleep(2)
            st.session_state.edit = ""
            switch_page("personen")
        



else:
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
