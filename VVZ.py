import streamlit as st
from pymongo import ASCENDING
from misc.config import *
from misc.util import *
from streamlit_option_menu import option_menu
import streamlit as st

# make all neccesary variables available to session_state
setup_session_state()

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
logo()

# Navigation in Sidebar anzeigen
display_navigation()

def edit(v_id):
    st.session_state.edit = v_id

# Eine Veranstaltung nach oben verschieben
def ver_move_up(v):
    target = veranstaltung.find_one( {"kategorie": v["kategorie"], "rang": {"$lt": v["rang"]}}, sort = [("rang",-1)])
    if target:
        n= target["rang"]
        veranstaltung.update_one(target, {"$set": {"rang": v["rang"]}})    
        veranstaltung.update_one(v, {"$set": {"rang": n}})    

def ver_move_down(v):
    target = veranstaltung.find_one({"kategorie": v["kategorie"],"rang": {"$gt": v["rang"]}}, sort = [("rang",+1)])
    if target:
        n= target["rang"]
        veranstaltung.update_one(target, {"$set": {"rang": v["rang"]}})    
        veranstaltung.update_one(v, {"$set": {"rang": n}})    

def name_of_sem_id(semester_id):
    x = semester.find_one({"_id": semester_id})
    return x["name_de"]

def name_of_ver_id(ver_id):
    x = veranstaltung.find_one({"_id": ver_id})
    return x["name_de"]

# Ab hier wird die Seite angezeigt
st.header("Veranstaltungsverzeichnis")

if st.session_state.logged_in:
    if st.session_state.edit == "":
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
                    col1, col2, col3, col4 = st.columns([1,1,3,20]) 
                    with col1:
                        st.button('↓', key=f'down-{v["_id"]}', on_click = ver_move_down, args = (v, ))
                    with col2:
                        st.button('↑', key=f'up-{v["_id"]}', on_click = ver_move_up, args = (v, ))
                    with col3:
                        st.button('Bearbeiten', key=f"edit-{v['_id']}", on_click = edit, args = (v["_id"], ))
                    with col4:
                        d = [(person.find_one({"_id": x}))["name"] for x in v["dozent"]]
                        st.write(f"{v['name']} ({', '.join(d)})")
    else:
        v = veranstaltung.find_one({"_id": st.session_state.edit})
        col1, col2 = st.columns([20,3])
        with col1:
            st.subheader(v["name_de"])
        with col2: 
            st.button('Bearbeiten', key=f'edit-{v["_id"]}', on_click = edit, args = ("", ))






    col1, col2, col3, col4 = st.columns([20,3,1,1]) 
    with col1:
        st.button("en" if st.session_state.lang == "de" else "de", on_click = change_lang)
    # Der Ausklapp-Umschalter
    with col2:
        st.button("Alles einklappen" if st.session_state.expand_all == True else "Alles ausklappen", on_click = change_expand_all)

    # Alle Kategorien. (ASCENDING sortiert sie nach ihrer Anzeige-Reihenfolge.)
    cats = list(category.find(sort=[("rang", pymongo.ASCENDING)]))

    # Nun werden für alle Kategorien all Frage-Antwort-Paare angezeigt
    for cat in cats:
        st.divider()
        st.write(cat["name_de"] if st.session_state.lang == "de" else cat["name_en"])
        y = qa.find({"category": cat["kurzname"]}, sort=[("rang", pymongo.ASCENDING)])
        for x in y:
            with st.expander(x["q_de"] if st.session_state.lang == "de" else x["q_en"], expanded = st.session_state.expand_all):
                stu1 = "Studiengänge" if st.session_state == "de" else "Study programs"
                stu2 = "alle" if st.session_state == "de" else "all"
                stu2 = (stu2 if x['studiengang'] == [] else (', '.join(x['studiengang'])))
                st.write(f"{stu1}: {stu2}")
                st.write("Antwort" if st.session_state == "de" else "Answer")
                st.write(x["a_de"] if st.session_state.lang == "de" else x["a_en"])
                if x["kommentar"] != "":
                    st.write("Kommentar:")
                    st.write(x["kommentar"])

else:
    placeholder = st.empty()
    with placeholder.form("login"):
        st.markdown("#### Login")
        kennung = st.text_input("Benutzerkennung")
        password = st.text_input("Passwort", type="password")
        submit = st.form_submit_button("Anmelden")
        st.session_state.user = kennung
        
    if submit and can_edit(st.session_state.user) and authenticate(kennung, password): 
        # If the form is submitted and the email and password are correct,
        # clear the form/container and display a success message
        placeholder.empty()
        st.session_state.logged_in = True
        st.success("Login successful")
        st.rerun()
    elif submit:
        st.error("Login failed")
        st.rerun()
    else:
        pass

st.sidebar.button("logout", on_click = logout)
