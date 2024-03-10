import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from misc.config import *
from misc.util import *

# make all neccesary variables available to session_state
setup_session_state()

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# Navigation in Sidebar anzeigen
display_navigation()

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:

    with st.expander("# Verwendete Variablen"):  
        st.write("Jedes Symbol repräsentiert eine _Collection_ in der Datenbank. Die Felder dieser Collection sind in den Aufzählungen bezeichnet. Taucht in dieser Aufzählung ein weiteres Symbol auf, so bedeutet das, dass die Collection an dieser Stelle auf eine andere Collection verweist. Eine eckige Klammer, etwa bei **Semester** [🎈 Veranstaltung] bezeichnet eine Liste. (Hier ist also ein Feld in der Collection _Semester_ gefüllt mit einer Liste aus Veranstaltungen.)")
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write("### 📅  Semester  \n* Name (de)  \n* Name (en)  \n* Kurzname  \n* Rang  \n* [🖉 Kategorie]  \n* [∞ Code]  \n* [🎈 Veranstaltung]")
        with col2:
            st.write("### 🖉 Kategorie  \n* Titel (de)  \n* Titel (en)  \n* Untertitel (de)  \n* Untertitel (en)  \n* Prefix (de)  \n* Prefix (en)  \n* Suffix (de)  \n* Suffix (en)  \n* Rang  \n* 📅 Semester  \n* [🎈 Veranstaltung]  \n* Kommentar")
        with col3: 
            st.write("### ∞ Code  \n* Name (de)  \n* Beschreibung (de)  \n* Beschreibung (en)  \n* Rang  \n* 📅 Semester  \n* [🎈 Veranstaltung]  \n* Kommentar")
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write("###  ⛺ Ort  \n* Name (de)  \n* Name (en)  \n* Kurzname  \n * 🏢 Gebäude \n* Raum  \n* Größe  \n* Rang  \n* Sichtbar  \n* Kommentar")
        with col2:
            st.write("### 🏢 Gebäude  \n* Name (de)  \n* Name (en)  \n* Kurzname  \n* Adresse  \n* Url  \n* Rang  \n* Sichtbar  \n* Kommentar")
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write("### 💁 Person  \n* Name (de)  \n* Name (en)  \n")
        with col2:
            st.write("### 🚌 Gruppe")
        with col3:
            st.write("### 🚻 Personen-Kategorie")
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write("### 📌 Studiengang  \n* Name (de)  \n* Name (en)  \n")
        with col2:
            st.write("### 🕮 Modul")
        with col3:
            st.write("### 🎉 Anforderung")
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write("### 🎈 Veranstaltung  \n* Name (de)  \n* Name (en)  \n")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
