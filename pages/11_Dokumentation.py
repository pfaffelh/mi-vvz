import streamlit as st
from streamlit_extras.switch_page_button import switch_page 

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

from misc.config import *
import misc.util as util
import misc.tools as tools

# make all neccesary variables available to session_state
# setup_session_state()

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    with st.expander("## Verwendete Variablen"):  
        st.write("Jedes Symbol repräsentiert eine _Collection_ in der Datenbank. Die Felder dieser Collection sind in den Aufzählungen bezeichnet. Taucht in dieser Aufzählung ein weiteres Symbol auf, so bedeutet das, dass die Collection an dieser Stelle auf eine andere Collection verweist. Eine eckige Klammer, etwa bei **Semester** [🎈 Veranstaltung] bezeichnet eine Liste. (Hier ist also ein Feld in der Collection _Semester_ gefüllt mit einer Liste aus Veranstaltungen.)")
        st.divider()
        st.markdown("### 🎈 Veranstaltung")
        st.markdown("Die Beschreibung von Veranstaltungen ist der Kern der ganzen App und hat vier Bereiche.")
        col1, col2, col3, col4 = st.columns([1,1,1,1])
        with col1:
            st.markdown("#### Grunddaten")
            st.markdown("Hier sind _Name_ (de und en), _midname_ (ein mittelkurzer Name) und _kurzname_ (ein Kurzname, der z.B. im Raumplan verwendet wird), _ECTS_ (die typische Anzahl an ECTS-Punkten für die Veranstaltung), _Kommentar für die Homepage_, und eine _URL_ gemeint, außerdem: ")
            st.markdown("📅  Semester", help = "Das Semester, in dem die Veranstaltung stattfindet.")
            st.markdown("🖉 Rubrik", help = "Die eindeutige Rubrik dieser Veranstaltung.")
            st.markdown("∞ Code", help = "Eine Liste von Codes, die für die Veranstaltung zutreffen.")
        with col2:
            st.markdown("#### Personen, Termine")
            st.markdown("Es gibt drei Listen von Personen:")
            st.markdown("[💁 Dozent*innen]", help = "Eine Liste an Dozent*innen für diese Veranstaltung.")
            st.markdown("[💁 Assistent*innen]", help = "Eine Liste an Assistent*innen für diese Veranstaltung.")
            st.markdown("[💁 Organisator*innen]", help = "Eine Liste an Organisator*innen für diese Veranstaltung.")
            st.markdown("Ein wöchentlicher Termine besteht aus _Art_ (z.B. Vorlesung), ⛺ _Raum_, _Wochentag_, _Beginn_, _Ende_, _Kommentar_. Von diesen wird eine Liste angelegt, wobei _Wochentag_, _Beginn_ und _Ende_ nicht belegt sein müssen. (_Raum_ muss belegt sein, aber es gibt einen leeren Raum.)")
            st.markdown("Einmalige Termine sind momentan in der Datenbank hinterlegt, jedoch in der App nicht befüllbar, da sie in einem eigenen Kalender verwaltet werden.")
        with col3: 
            st.markdown("#### Kommentiertes Vorlesungsverzeichnis")
            st.markdown("Hier werden Informationen hinterlegt, etwa (jeweils de und en) _Inhalt_, _Literatur_, _Vorkenntnisse_, und ein _Kommentar_.")
        with col4: 
            st.markdown("#### Verwendbarkeit")
            st.markdown("Hier werden Möglichkeiten beschrieben, in welchen Modulen die Veranstaltung ECTS-Punkte liefern kann. Dafür werden Anforderungen beschrieben, etwa Bestehen einer Klausur, oder Erreichen einer gewissen Punktzahl bei den Übungsaufgaben. Für diese Beschreibung benötigen wir drei Listen:")
            st.markdown("[🕮 Modul]", help = "Liste der Module, in denen die Veranstaltung eingesetzt werden kann.")
            st.markdown("[🕮 Anforderung]", help = "Liste der möglichen Anforderungen in den einzelnen Modulen.")
            st.markdown("[(🕮 Modul, 🕮 Anforderung)]", help = "Liste aus Tupeln aus Modul und Anforderung. Werden alle Anforderungen erfüllt, kann die Veranstaltung im entsprechenden Modul verbucht werden.")            
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.markdown("### 🖉 Rubrik")
            st.markdown("(einer Veranstaltung.) Es gibt Felder (jeweils auf deutsch (de) und englisch (en) mit der Reihenfolge in der Anzeige einer Rubrik:  \n* Prefix  \n* Titel  \n* Untertitel  \n* Suffix")
            st.markdown("Weiter gibt es die Variablen (Erklärung siehe bei Semester) _Rang_ und _hp_sichtbar_ sowie _Kommentar_ für den internen Gebrauch.")
            st.markdown(" 📅 Semester", help = "Das eindeutige Semester, in dem es diese Rubrik gibt")
            st.markdown("[🎈 Veranstaltung]", help = "Eine Liste von Veranstaltungen, die zu dieser Rubrik gehören.")
        with col2: 
            st.markdown("### ∞ Code")
            st.markdown("(einer Veranstaltung.) Hier ist _Name_ ein Kürzel, der _Beschreibung_ abkürzen soll. (Letzteres gibt es in de und en.) Wieder gibt es _Rang_, _hp_sichtbar_ und _kommentar_. Wie bei _Rubrik_ gibt es:")
            st.markdown("📅 Semester", help =  "Das eindeutige Semester, in dem es diesen Code gibt")
            st.markdown("[🎈 Veranstaltung]", help = "Eine Liste von Veranstaltungen des entsprechenden Semesters, die diesen Code tragen.")
        with col3:
            st.markdown("### 📅  Semester")
            st.markdown("Es gibt _Name_ (de und en), jeweils Langnamen für das Semester.")
            st.markdown("Ein _Kurzname_ (z.B. 2024SS), wird in vielen Anzeichen verwendet, und auch zum Sortieren der Semester.")
            st.markdown("Ein _Rang_ ergibt die Reihenfolge in einer geordneten Liste von Semestern.")
            st.markdown("_hp_sichtbar_ gibt an, ob das Semester auf der Homepage angezeigt werden soll. _False_, falls dieses Semester schon zu lange her ist.")
            st.markdown("[🖉 Rubrik]", help="Gibt eine Liste der _identifier_ der Rubriken an (z.B. 1a. Grundvorlesungen), die es in diesem Semester gibt.")
            st.markdown("[∞ Code]", help="Gibt eine Liste der _identifier_ der Codes an (z.B. B: Pflicht im BSc), die es in diesem Semester gibt.")
            st.markdown("[🎈 Veranstaltung]", help="Gibt eine Liste der _identifier_ der Veranstaltungen an, die es in diesem Semester gibt.")
        st.divider()
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.markdown("### ⛺ Raum")
            st.markdown("_Name_ (de und en) und _Kurzname_ beschreiben den Raum. Der _Kurzname_ wird dabei z.B. in den Darstellungen der Veranstaltungen eines Semesters verwendet. Die _Größe_ gibt die Anzahl der verfügbaren Sitzplätze an, und es gibt ein Feld _Kommentar_. _sichtbar_ gibt die Verfügbarkeit in Auswahllisten an.")
            st.markdown("🏢 Gebäude", help = "Das Gebäude, in dem sich der Raum befindet.")
        with col2:
            st.markdown("### 🏢 Gebäude")
            st.markdown("Es gibt die Felder _Name_ (de und en), _Kurzname_, _Adresse_, _Url_ (für einen Link in einer Karte), sowie _Rang_, _sichtbar_ und _kommentar_.")
        with col3:
            st.markdown("### 💁 Person")
            st.markdown("Es gibt die selbsterklärenden Felder _Name_, _Vorname_, _titel_, _tel_ und _email_. Der _name_prefix_ ist zumeist eine Abkürzung des Vornames und wird bei der Semesterdarstellung verwendet. Die Bool'schen Variablen _sichtbar_ und _hp_sichtbar_ geben die Sichtbarkeit an. Der _Kurzname_ wir zwar weitergeführt, wird aber nicht mehr verwendet.")
            st.markdown("[🎈 Veranstaltung]", help = "Eine Liste der Veranstaltungen, die mit der Person in Verbindung stehen.")
            st.markdown("[📅  Semester]", help = "Eine Liste der Semester, die die Person am Mathematischen Institut verbracht hat (und dort Lehre gemacht hat).")
        st.divider()
        col1, col2, col3, col4 = st.columns([1,1,1,1])
        with col1:
            st.markdown("### 📌 Studiengang")
            st.markdown("_Name_ und _Kurzname_ bezeichnen den Studiengang. (Den Namen gibt es nur in einer Sprache, da es der offizielle Name sein sollte. Der _Kurzname_ wird bei Darstellungen bevorzugt verwendet. _sichtbar_ gibt an, ob der Studiengang in Auswahlmenüs wählbar ist. _rang_ gibt die Reihenfolge in einer geordneten Liste, _kommentar_ einen internen Kommentar an.)")
            st.markdown("[🕮 Modul]", help = "Eine Liste von Modulen, die es in diesem Studiengang gibt.")
        with col2:
            st.markdown("### 🕮 Modul")
            st.markdown("Ebenfalls gibt es hier Felder _kurzname_, _sichtbar_, _Name_ (de und en), _rang_ und _kommentar.")
            st.markdown("[📌 Studiengang]", help = "Eine Liste von Studiengängen, die dieses Modul enthalten.")
        with col3:
            st.markdown("### 🎉🖉 Anforderungs-kategorie")
            st.markdown("Eigentlich gibt es nur drei Instanzen, nämlich *PL*, *SL* und *Kommentar*. Jede Anforderung wird hierbei durch eine solche Kategorie beschrieben. Diese enthält die Felder _Name_ (de und en), _rang_, _sichtbar_ und _kommentar_.")
        with col4: 
            st.markdown("### 🎉 Anforderung")
            st.markdown("Hier wird eine Anforderung beschrieben. Dies wird bei einer Veranstaltung benötigt um zu beschreiben, was ein Studierender tun muss, um ECTS-Punkte zu erhalten. Es gibt die Felder _Name_ (de und en), _sichtbar_, _kommentar_ und _rang_, sowie")
            st.markdown("🎉🖉 Anforderungskategorie", help = "Die Kategorie einer Anforderung.")

    with st.expander("# Change Log"):
        st.markdown("2024/05/01: Version 0.1")

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
