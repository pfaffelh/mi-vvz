import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, timedelta
from io import BytesIO
import pymongo
import pandas as pd

# Transform df to xls
def to_excel(df):
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']

        # Automatische Anpassung der Spaltenbreite an die Inhalte
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter  # Spaltenbuchstabe (z.B., 'A', 'B', 'C')
            for cell in col:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = max_length + 2  # +2 für Puffer
            worksheet.column_dimensions[col_letter].width = adjusted_width
    return output.getvalue()


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
st.session_state.page = "Suchen"

if st.session_state.logged_in:
    st.header("Suche nach Veranstaltungen / Terminen")
    with st.expander("Suche nach Veranstaltungen..."):
        st.write("...auf die folgendes zutrifft:")
        st.write("(Die einzelnen Zeilen sind mit 'und' verknüpft. Die eingegebenen Wörter im Textfeld sind mit 'oder' verknüpft.)")
        # QUERY
        # Auswahl von Semester
        semesters = list(util.semester.find(sort=[("rang", pymongo.DESCENDING)]))
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.write("von...")
            semester_id_von = st.selectbox(label="von", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_von")
            semester_von = util.semester.find_one({"_id": semester_id_von})
        with col2:
            st.write("...bis...")
            semester_id_bis = st.selectbox(label="bis", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "semester_bis")
            semester_bis = util.semester.find_one({"_id": semester_id_bis})
        semester_auswahl = list(util.semester.find({"rang": {"$gte": semester_von["rang"], "$lte": semester_bis["rang"]}}))

        # Auswahl von Rubriken 
        rubrik_vorauswahl = list(util.rubrik.find({"semester": {"$in": [x["_id"] for x in semester_auswahl]}, "veranstaltung": {"$ne": []}}, sort = [("titel_de", pymongo.ASCENDING)]))
        rubrik_list = st.multiselect("Rubriken", [x["_id"] for x in rubrik_vorauswahl], [], format_func = (lambda a: tools.repr(util.rubrik, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchte Veranstaltung muss einen der ausgewählten Rubriken tragen. Falls keine Rubrik angegeben ist, werden Rubriken in der Suche nicht berücksichtigt.")

        # Auswahl von Codes
        code_vorauswahl = list(util.code.find({"semester": {"$in": [x["_id"] for x in semester_auswahl]}, "veranstaltung": {"$ne": []}}, sort = [("beschreibung_de", pymongo.ASCENDING)]))
        code_list = st.multiselect("Codes", [x["_id"] for x in code_vorauswahl], [], format_func = (lambda a: tools.repr(util.code, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchten Veranstaltungen müssen einen der ausgewählten Codes tragen. Falls kein Code angegeben ist, werden Codes in der Suche nicht berücksichtigt.")

        # Auswahl von Personen
        person_vorauswahl = list(util.person.find({"semester": {"$elemMatch": {"$in": [x["_id"] for x in semester_auswahl]}}, "veranstaltung": {"$ne": []}}, sort = [("name", pymongo.ASCENDING)]))
        person_list = st.multiselect("Personen", [x["_id"] for x in person_vorauswahl], [], format_func = (lambda a: tools.repr(util.person, a, False, False)), placeholder = "Bitte auswählen", help = "Die gesuchten Veranstaltungen müssen mit einer der ausgewählten Personen verbunden sein. Falls kein Code angegeben ist, werden Codes in der Suche nicht berücksichtigt.")

        # Freitextsuche im Titel
        te = st.text_input("Titel enthält", help = "Es wird nach ganzen Wörtern mit einer oder-Verknüpfung gesucht")

        # Erstellung der Query
        query = {}
        query["semester"] = {"$in": [x["_id"] for x in semester_auswahl]}
        if code_list:
            query["code"] = {"$elemMatch": { "$in": code_list}}
        if rubrik_list:
            query["rubrik"] = {"$in": rubrik_list}
        if person_list:
            query["$or"] = [{"dozent": {"$elemMatch": { "$in": person_list}}}, {"assistent": {"$elemMatch": { "$in": person_list}}}, {"organisation": {"$elemMatch": { "$in": person_list}}}]
        if te:
            query["$text"] = {"$search": f'{te}'}

        result = list(util.veranstaltung.find(query))

        st.divider()
        st.write("Folgende Felder werden ausgegeben")
        # Auswahl der Ausgabe
        col1, col2, col3, col4 = st.columns([1,1,1,1])
        with col1:
            ausgabe_semester = st.checkbox("Semester", True, key = "semester1")
        with col2:
            ausgabe_rubrik = st.checkbox("Rubrik", True)
        ausgabe_titel = True
        with col3:
            ausgabe_dozent = st.checkbox("Dozent*innen", True, key = "dozent1")
        with col4:
            ausgabe_assistent = st.checkbox("Assistent*innen", True)

        semester = [tools.repr(util.semester, r["semester"], False, True) for r in result]
        titel = [r["name_de"] for r in result]
        rubrik = [tools.repr(util.rubrik, r["rubrik"], False, True) for r in result]
        titel = [r["name_de"] for r in result]
        dozent = [", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in [util.person.find_one({"_id": p}) for p in r["dozent"]]]) for r in result]
        assistent = [", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in [util.person.find_one({"_id": p}) for p in r["assistent"]]]) for r in result]

        dict = {}
        if ausgabe_semester:
            dict["Semester"] = semester
        if ausgabe_rubrik:
            dict["Rubrik"] = rubrik
        dict["Veranstaltung"] = titel    
        if ausgabe_dozent:
            dict["Dozent*innen"] = dozent
        if ausgabe_assistent:
            dict["Assistent*innen"] = assistent

        df = pd.DataFrame(dict)
        felder = (["Semester"] if ausgabe_semester else []) + (["Rubrik"] if ausgabe_rubrik else []) + ["Veranstaltung"]
        felder_as = ([False] if ausgabe_semester else []) + ([True] if ausgabe_rubrik else []) + [True]
        df = df.sort_values(by=felder, ascending = felder_as)

        st.divider()

        st.data_editor(df, use_container_width=True, hide_index=True)   
        # xls Export
        output = BytesIO()
        excel_data = to_excel(df)
        st.download_button(
            label="Download Excel-Datei",
            data=excel_data,
            file_name="veranstaltungen.xls",
            mime="application/vnd.ms-excel"
        )

    with st.expander("Suche nach einmaligen Terminen..."):
        st.write("")
        col1, col2 = st.columns([1,1])
        anzeige_start = col1.date_input("von", value = datetime.now() + timedelta(days = -30), format="DD.MM.YYYY")
        anzeige_ende = col2.date_input("bis", value = datetime.now() + timedelta(days = 90), format="DD.MM.YYYY")

        # nur_cal = st.toggle("Genau die Termine aus dem Prüfungskalender", True)
        ter_list = [ta["_id"] for ta in list(util.terminart.find({"cal_sichtbar" : True}))]
        ta_list = st.multiselect("Als Default werden genau die Terminarten aus dem Prüfungskalender gesucht.", [x["_id"] for x in list(util.terminart.find())], ter_list, format_func = (lambda a: tools.repr(util.terminart, a, False, False)), placeholder = "Bitte auswählen")

        st.divider()
        st.write("Folgende Felder werden ausgegeben")
        # Auswahl der Ausgabe
        col1, col2, col3, col4 = st.columns([1,1,1,1])
        with col1:
            ausgabe_semester = st.checkbox("Semester", True, key = "semester2")
        with col2:
            ausgabe_veranstaltung = st.checkbox("Veranstaltung", True)
        ausgabe_terminart = True
        ausgabe_termin = True
        with col3:
            ausgabe_dozent = st.checkbox("Dozent*innen", True, key = "dozent2")


        anzeige_start = datetime.combine(anzeige_start, datetime.min.time())
        anzeige_ende = datetime.combine(anzeige_ende, datetime.max.time())
        
        ver = list(util.veranstaltung.find({"einmaliger_termin" : { "$elemMatch" : {  "key" : { "$in" : ta_list}, "startdatum" : { "$gte" : anzeige_start}, "startdatum" : { "$lte" : anzeige_ende }}}}))

        all = []

        for v in ver:
            d = {}
            for t in v["einmaliger_termin"]:
                if t["startdatum"] is not None and t["startdatum"] <= anzeige_ende and t["enddatum"] is not None and t["enddatum"] >= anzeige_start and t["key"] in ta_list:
                    if ausgabe_semester:
                        d["Semester"] = tools.repr(util.semester, v["semester"], False, True)
                    if ausgabe_veranstaltung:
                        d["Veranstaltung"] = tools.repr(util.veranstaltung, v["_id"], False, True)
                    if ausgabe_dozent:
                        d["Dozent"] = ", ".join([f"{c['name_prefix']} {c['name']}".strip() for c in [util.person.find_one({"_id": p}) for p in v["dozent"]]])
                    d["Terminart"] = tools.repr(util.terminart, t["key"], False, True) + " " + t[f"kommentar_de_html"]
                    d["Einmaliger Termin Anfang"] = datetime.combine(t["startdatum"].date(), t["startzeit"].time())
                    d["Einmaliger Termin Ende"] = datetime.combine(t["enddatum"].date(), t["endzeit"].time())
                    all.append(d)
                d = {}
        
        df = pd.DataFrame.from_records(all)
        df = df.sort_values(by="Einmaliger Termin Anfang")
#        df["Einmaliger Termin"] = [d.strftime('%d.%m.%Y  %H:%M') for d in df["Einmaliger Termin"]]
        st.divider()
        st.data_editor(df, use_container_width=True, hide_index=True)   
        # Streamlit-Button für den Download
        output = BytesIO()
        excel_data = to_excel(df)
        st.download_button(
            label="Download Excel-Datei",
            data=excel_data,
            file_name="termine.xls",
            mime="application/vnd.ms-excel"
        )

    with st.expander("Deputate"):
        st.write("Hier werden gesammelt die Deputate für das aktuelle Semester ausgegeben")
        ver = util.veranstaltung.find({"semester" : st.session_state.semester_id})

        data = []
        for v in ver:
            for p in v["dozent"] + v["assistent"] + v["organisation"]:
                rolle = "Dozent*in" if p in v["dozent"] else ("Assistent*in" if p in v["assistent"] else "Organisation")
                try :
                    sws = [d["sws"] for d in v["deputat"] if d["person"] == p][0]
                    kommentar = [d["kommentar"] for d in v["deputat"] if d["person"] == p][0]
                    kommentar_intern = [d["kommentar_intern"] for d in v["deputat"] if d["person"] == p][0]
                except:
                    sws = 0
                    kommentar = ""
                    kommentar_intern = ""
                data.append({
                    "person": tools.repr(util.person, p, False, True),
                    "veranstaltung": tools.repr(util.veranstaltung, v["_id"], False, True),
                    "rolle": rolle,
                    "sws": sws,
                    "kommentar": kommentar,
                    "kommentar_intern": kommentar_intern
                    })

            for t in v["woechentlicher_termin"] + v["einmaliger_termin"]:
                try :
                    sws = [d["sws"] for d in v["deputat"] if d["person"] == p][0]
                    kommentar = [d["kommentar"] for d in v["deputat"] if d["person"] == p][0]
                    kommentar_intern = [d["kommentar_intern"] for d in v["deputat"] if d["person"] == p][0]
                except:
                    sws = 0
                    kommentar = ""
                    kommentar_intern = ""
                for p in t["person"]:
                    data.append({
                        "person": tools.repr(util.person, p, False, True),
                        "veranstaltung": tools.repr(util.veranstaltung, v["_id"], False, True),
                        "rolle": tools.repr(util.terminart, t["key"], False, True),
                        "sws": [d["sws"] for d in v["deputat"] if d["person"] == p][0],
                        "kommentar": [d["kommentar"] for d in v["deputat"] if d["person"] == p][0],
                        "kommentar_intern": [d["kommentar_intern"] for d in v["deputat"] if d["person"] == p][0]
                        })
        df = pd.DataFrame.from_records(data)
        df = df.sort_values(by = ['person', 'veranstaltung'])
        st.dataframe(df, hide_index = True, use_container_width = True)
        output = BytesIO()

        # Streamlit-Button für den Download
        excel_data = to_excel(df)
        st.download_button(
            label="Download Excel-Datei",
            data=excel_data,
            file_name="deputate.xls",
            mime="application/vnd.ms-excel"
        )




else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
