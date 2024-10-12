import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pymongo
import time
import ldap
import misc.util as util
import misc.latex as latex
from bson import ObjectId
from misc.config import *
import pandas as pd
import json, jinja2
import subprocess

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

from misc.config import *
import misc.util as util
import misc.tools as tools

tools.delete_temporary()

# Navigation in Sidebar anzeigen
tools.display_navigation()
st.session_state.page = "LaTeX"

sem_id = st.session_state.semester_id
sem = util.semester.find_one({"_id" : sem_id})
sem_kurzname = sem["kurzname"]

if st.session_state.logged_in:
    st.header("Ausgabe von LaTeX-Files")
    st.write("Hier können LaTeX-Files für das kommentierte Vorlesungsverzeichnis und die Erweiterungen der Modulhandbücher ausgegeben werden.")
    # Zunächst ein paar Einstellungen

    col0, col1 = st.columns([1,1])
    with col0:
        which = st.selectbox("Was soll erstellt werden?", ["Kommentiertes Vorlesungsverzeichnis", "Erweiterung der Modulhandbücher"], index = None, placeholder = "Bitte auswählen")
        kommentare = True if which == "Kommentiertes Vorlesungsverzeichnis" else False
        erweiterung = not kommentare
    with col1: 
        la = st.selectbox("Sprache", ["deutsch", "englisch"], index = None, placeholder = "Bitte auswählen")

    en = True if la == "englisch" else False
    lang = "en" if en else "de"

    #alter = st.toggle("Andere Sprache verwenden, falls Kommentare nicht verfügbar", value=True, help="Andernfalls bleibt der Inhalt im Kommentierten Vorlesungsverzeichnis leer.")
    alter = True

    # komm = st.toggle("Nur Veranstaltungen ausgeben, die den Code _Komm_ tragen", value=True, help="Andernfalls werden alle Veranstaltungen des Semesters ausgegeben.")
    komm = True

    # include_inhalt = st.toggle("Inhalt der Veranstaltungen anzeigen", value=True, help="Andernfalls werden nur Verwendbarkeiten ausgegeben.")
    include_inhalt = True

    # verw_kurz = st.toggle("Verwendbarkeiten nur in Kurzform ausgeben", value=True, help="Andernfalls wird die komplette Verwendbarkeitsmatrix für jede Veranstaltung ausgegeben.")

    verw_kurz = True if kommentare else False

    wasserzeichen = st.text_input('Wasserzeichen, z.B. Vorläufige Version', "", key = "watermark")

    with st.expander("Vorspann (LaTeX)"):
        vorspann = st.text_area("Vorspann mit LaTeX-Befehlen", sem[f"vorspann_kommentare_{lang}"], height = 200 )
        submit = st.button("Speichern")
        if submit:
            util.semester.update_one({"_id" : sem_id}, { "$set" : {f"vorspann_kommentare_{lang}" : vorspann }})
            st.success("Vorspann gespeichert.")

    # includefile = st.text_input('Zusätzliches tex-File, das eingebunden werden soll', f"Kommentare_{sem_kurzname}-vorspann-{'en' if en else 'de'}.tex", key = "includefile")

    titel = ("Kommentiertes Vorlesungsverzeichnis" if kommentare else "Ergänzungen des Modulhandbuchs") if not en else ("Comments on the course catalogue" if kommentare else "Supplements of the module handbooks")

    if komm:
        sem_name = util.semester.find_one({"_id" : sem_id})[f"name_{'en' if en else 'de'}"]
        sem_id = st.session_state.semester_id
        komm_id = util.code.find_one({"semester" : sem_id, "name" : { "$eq" : "Komm" }})["_id"]
        ver_komm = list(util.veranstaltung.find({"semester" : sem_id, "code" : { "$elemMatch" : { "$eq" : komm_id }}}))
    else:
        ver_komm = list(util.veranstaltung.find({"semester" : sem_id}))

    data = latex.makedata(sem_kurzname, komm, "en" if en else "de", alter)
    data["semester"] = sem_name
    data["titel"] = titel
    data["wasserzeichen"] = wasserzeichen
    data["include_inhalt"] = include_inhalt
    data["lang"] = "en" if en else "de"
    data["alter"] = alter
    data["komm"] = komm
    data["verw_kurz"] = verw_kurz
    data["vorspann"] = vorspann
    
    template = latex.latex_jinja_env.get_template(f"static/template.tex")
    kommentare = template.render(data = data)

    file_name = f"{sem_kurzname}_{data['lang']}" if kommentare else f"{sem_kurzname}mh_{data['lang']}"

    # Beides muss ausgewählt sein, bevor ein tex erzeugt wird
    if which and la:

        col0, col1 = st.columns([1,1])
        col0.download_button("Download (.tex)", kommentare, file_name=file_name + ".tex", help=None, on_click=None, args=None, kwargs=None, type = 'primary')
        with open('texfiles/' + file_name + '.tex', 'w') as file:
            file.write(kommentare) 

        command = ['pdflatex', '-interaction=nonstopmode', '-output-directory', 'texfiles', f'texfiles/{file_name}.tex']
        result = subprocess.run(command, capture_output=True, text = True)

        try:
            with open('texfiles/' + file_name + '.pdf', 'rb') as file:
                pdf = file.read()
                col1.download_button("Download (.pdf)", pdf, file_name=file_name + '.pdf', help=None, on_click=None, args=None, kwargs=None, type = 'primary', mime='pdf')
        except FileNotFoundError:
            st.error("pdf-Datei nicht vorhanden.")

        with st.expander("LaTeX output"):
            st.write(result.stdout)  # This prints the output from pdflatex
            st.write(result.stderr)  # 

    if komm:
        st.write("Es werden nur Veranstaltungen aufgenommen, die den Code 'Komm' tragen.")
        sem_id = st.session_state.semester_id
        komm_id = util.code.find_one({"semester" : sem_id, "name" : { "$eq" : "Komm" }})["_id"]
        ver_komm = list(util.veranstaltung.find({"semester" : sem_id, "code" : { "$elemMatch" : { "$eq" : komm_id }}}))
        ver_text = list(util.veranstaltung.find({"semester" : sem_id, "$or" : [{ "inhalt_de" : { "$ne" : ""}}, {"inhalt_en" : { "$ne" : ""}}]}))

        # Veranstaltungen, die den Code Komm haben, für die kein Kommentar vorhanden ist
        Delta1 = [tools.repr(util.veranstaltung, v["_id"], False) for v in ver_komm if v not in ver_text]
        # Veranstaltungen, für die ein Kommentar vorhanden ist, die aber den Code Komm nicht tragen
        Delta2 = [tools.repr(util.veranstaltung, v["_id"], False) for v in ver_text if v not in ver_komm]

        if Delta1 != []:
            st.write("#### Veranstaltungen mit Code _Komm_, für die kein Kommentar vorhanden ist")
            for v in Delta1:
                st.write(v)
        else:
            st.write("#### Alle Veranstaltungen mit Code _Komm_ verfügen über einen Kommentar.")

        if Delta2 != []:
            st.write("#### Veranstaltungen mit Kommentar, die den Code _Komm_ nicht besitzen")
            for v in Delta2:
                st.write(v)
        else:
            st.write("#### Alle Veranstaltungen mit Kommentar haben Code _Komm_.")

