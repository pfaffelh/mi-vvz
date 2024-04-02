import streamlit as st
from streamlit_extras.switch_page_button import switch_page 

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
from misc.util import *
import misc.tools as tools

# make all neccesary variables available to session_state
setup_session_state()

# Navigation in Sidebar anzeigen
display_navigation()

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    with st.expander("## Verwendete Variablen"):  
        st.write("Jedes Symbol repräsentiert eine _Collection_ in der Datenbank. Die Felder dieser Collection sind in den Aufzählungen bezeichnet. Taucht in dieser Aufzählung ein weiteres Symbol auf, so bedeutet das, dass die Collection an dieser Stelle auf eine andere Collection verweist. Eine eckige Klammer, etwa bei **Semester** [🎈 Veranstaltung] bezeichnet eine Liste. (Hier ist also ein Feld in der Collection _Semester_ gefüllt mit einer Liste aus Veranstaltungen.)")
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.markdown("### 📅  Semester")
            st.markdown("Name (de)", help="Gibt einen Langnamen für das Semester auf deutsch")
            st.markdown("Name (en)", help="Gibt einen Langnamen für das Semester auf englisch")
            st.markdown("Kurzname", help="Gibt einen Kurznamen (z.B. 2024SS) für das Semester, wird in vielen Anzeichen verwendet, und auch zum Sortieren der Semester.")
            st.markdown("Rang", help="Gibt einen Rang in einer geordneten Liste von Semestern.")
            st.markdown("hp_sichtbar", help="Gibt an, ob das Semester auf der Homepage angezeigt werden soll. _False_, falls dieses Semester schon zu lange her ist.")
            st.markdown("[🖉 Kategorie]", help="Gibt eine Liste der _identifier_ der Kategorien an (z.B. 1a. Grundvorlesungen), die es in diesem Semester gibt.")
            st.markdown("[∞ Code]", help="Gibt eine Liste der _identifier_ der Codes an (z.B. B: Pflicht im BSc), die es in diesem Semester gibt.")
            st.markdown("[🎈 Veranstaltung]", help="Gibt eine Liste der _identifier_ der Veranstaltungen an, die es in diesem Semester gibt.")
        with col2:
            st.markdown("### 🖉 Kategorie")
            st.markdown("Es gibt Felder (jeweils auf deutsch (de) und englisch (en) mit der Reihenfolge in der Anzeige einer Kategorie:  \n* Prefix  \n* Titel  \n* Untertitel  \n* Suffix")
            st.markdown("Weiter gibt es die Variablen (Erklärung siehe bei Semester) _Rang_ und _hp_sichtbar_ sowie:")
            st.markdown(" 📅 Semester", help = "Das eindeutige Semester, in dem es diese Kategorie gibt")
            st.markdown("[🎈 Veranstaltung]", help = "Eine Liste von Veranstaltungen, die zu dieser Kategorie gehören.")
            st.markdown("Kommentar", help = "Ein beliebiger Kommentar, für internen Gebrauch.")
        with col3: 
            st.markdown("### ∞ Code")
            st.markdown("Hier ist _Name_ ein Kürzel, der _Beschreibung_ abkürzen soll. (Letzteres gibt es in de und en.) Wieder gibt es _Rang_, _hp_sichtbar_ und _kommentar_. Wie bei _Kategorie_ gibt es:")
            st.markdown("📅 Semester", help =  "Das eindeutige Semester, in dem es diesen Code gibt")
            st.markdown("[🎈 Veranstaltung]", help = "Eine Liste von Veranstaltungen des entsprechenden Semesters, die diesen Code tragen.")
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.markdown("### ⛺ Raum")
            st.markdown("_Name_ (de und en) und _Kurzname_ beschreiben den Raum. Der _Kurzname_ wird dabei z.B. in den Darstellungen der Veranstaltungen eines Semesters verwendet.")
            st.markdown("🏢 Gebäude", help = "Das Gebäude, in dem sich der Raum befindet.")
            st.markdown("Größe", help = "Gibt die Anzahl der Sitzplätze an.")
            st.markdown("_sichtbar_  \n* Kommentar")
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
    with st.expander("# Change Log"):
        st.markdown("2024/05/01: Version 0.1")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
