import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import datetime 
import pymongo

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
import misc.util as util
import misc.tools as tools

tools.delete_temporary()

# load css styles
from misc.css_styles import init_css
init_css()

# make all neccesary variables available to session_state
# setup_session_state()

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("VVZ")

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
collection = util.veranstaltung
st.session_state.page = "Raumplan"
st.session_state.edit = ""

semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
slotstart = [8, 10, 12, 14, 16, 18]
raum_dict = {r["_id"]: tools.repr(util.raum, r["_id"], show_collection = False) for r in util.raum.find() }
st.write(raum_dict.keys())
# Ab hier wird die Seite angezeigt
if st.session_state.logged_in:
    #with open("misc/styles.css") as f:
    #    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)
    st.header("Raumplan")
#    sem_id = st.selectbox(label="Semester", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.current_semester_id), format_func = (lambda a: util.semester.find_one({"_id": a})["name_de"]), placeholder = "Wähle ein Semester", label_visibility = "collapsed")
#    st.session_state.semester = sem_id
    if st.session_state.semester_id is not None:
        kat = list(util.rubrik.find({"semester": st.session_state.semester_id}, sort=[("rang", pymongo.ASCENDING)]))
        st.write(util.hauptraum_ids)
        raum_list = st.multiselect("Räume", raum_dict.keys(), util.hauptraum_ids, format_func = (lambda a: raum_dict[a]), placeholder = "Bitte auswählen")
        st.write("<hr style='height:1px;margin:0px;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
        showraum = [util.raum.find_one({"_id": id}) for id in raum_list]
        co = st.columns([1, 1] + [1 for s in slotstart])
        for i, s in enumerate(slotstart):
            with co[i+2]:
                st.markdown(f"{s}-{s+2}")
        for tag in tage:                        
            for j, r in enumerate(showraum):
                if j==0:
                    st.write("<hr style='height:1px;margin:0px;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
                co = st.columns([1, 1] + [1 for s in slotstart])
                with co[0]:
                    if j==0:
                        st.markdown(tag)
                with co[1]:
                    st.markdown(r["kurzname"])
                for k, s in enumerate(slotstart):
                    with co[k+2]:
                        # finde alle woechentliche_termine für den angezeigten Slot
                        ve = list(util.veranstaltung.find({"semester": st.session_state.semester_id, "woechentlicher_termin": {"$elemMatch": {"wochentag": {"$eq": tag}, "raum": r["_id"], "start": {"$gte": datetime.datetime(year = 1970, month = 1, day = 1, hour = s, minute = 0), "$lt": datetime.datetime(year = 1970, month = 1, day = 1, hour = s+2, minute = 0)}}}}))
                        for x in ve:
                            wt = x["woechentlicher_termin"]
                            w = list(filter(lambda w: w['wochentag'] == tag and w['raum'] == r["_id"] and w["start"] >= datetime.datetime(year = 1970, month = 1, day = 1, hour = s, minute = 0) and w["start"] < datetime.datetime(year = 1970, month = 1, day = 1, hour = s+2, minute = 0), wt))[0]
                            k = wt.index(w)
                            st.markdown("""
                                <style>
                                [data-testid=column] [data-testid=stVerticalBlock]{
                                    gap: 0rem;
                                    padding: 0rem;
                                }
                                </style>
                                """,unsafe_allow_html=True)
                            submit = st.button(f"**{x['kurzname']}**", type = "primary" if len(ve) > 1 else "secondary", help = tools.repr(util.veranstaltung, x["_id"], False), key = f"edit_{k}_{x['_id']}", use_container_width=True)
                            if submit:
                                st.session_state.edit = x["_id"]
                                st.session_state.page = "Veranstaltung"
                                st.session_state.expanded = "termine"
                                switch_page("veranstaltungen edit")

        #showraum = [r for i, r in enumerate(hauptraum) if show[i]]
        #co = st.columns([1,3,3,3,3,3])
        #for i, tag in enumerate(tage):
        #    with co[i+1]:
        #        st.markdown(tag)
        #        col = st.columns([1 for r in showraum])
        #        for j, r in enumerate(showraum):
        #            with col[j]:
        #                st.markdown(kurzkurzname[r["kurzname"]])
        # show raumplan
        # for s in slotstart:
        #     co = st.columns([1,3,3,3,3,3])
        #     with co[0]:
        #         st.markdown(f"{s}-{s+2}")
        #     for i, tag in enumerate(tage):
        #         with co[i+1]:
        #             col = st.columns([1 for r in showraum])
        #             for j, r in enumerate(showraum):
        #                 with col[j]:
        #                     # find termine veranstal
        #                     ve = list(veranstaltung.find({"semester": sem_id, "woechentlicher_termin": {"$elemMatch": {"wochentag": {"$eq": tag}, "raum": r["_id"], "start": {"$eq": datetime.datetime(year = 1970, month = 1, day = 1, hour = s, minute = 0)}}}}))
        #                     for x in ve:
        #                         wt = x["woechentlicher_termin"]
        #                         w = list(filter(lambda w: w['wochentag'] == tag and w['raum'] == r["_id"] and w["start"] == datetime.datetime(year = 1970, month = 1, day = 1, hour = s, minute = 0), wt))[0]
        #                         k = wt.index(w)
        #                         st.markdown("""
        #                             <style>
        #                             [data-testid=column] [data-testid=stVerticalBlock]{
        #                                 gap: 0rem;
        #                                 padding: 0rem;
        #                             }
        #                             </style>
        #                             """,unsafe_allow_html=True)
        #                         st.button(f"**{x['kurzname']}**", on_click=edit, args=(x["_id"],), type = "primary" if len(ve) > 1 else "secondary", help = tools.repr(veranstaltung, x["_id"], False), key = f"edit_{k}_{x['_id']}")

#                st.markdown("<style>.st-emotion-cache-f4k0dr { min-height: 0pt; gap: 0rem; }</style>", unsafe_allow_html=True)
#                st.markdown("<style>.st-emotion-cache-ocqkz7 { min-height: 0pt; line-height: 1; padding: 0rem; margin-bottom: 0rem; gap: 0rem; }</style>", unsafe_allow_html=True)
#                st.markdown("<style>.st-emotion-cache-zooq7g { min-height: 0pt; line-height: 1; padding: 0rem; margin-bottom: 0rem; gap: 0rem; }</style>", unsafe_allow_html=True)
#                st.markdown("<style>p { margin: 0px !important; }</style>", unsafe_allow_html=True)
#                st.markdown("<style>.st-emotion-cache-jp0p2n  { gap: 0rem; }</style>", unsafe_allow_html=True)

#                st.markdown("<style>.st-emotion-cache-eqffof { margin-bottom: 0rem; }</style>", unsafe_allow_html=True)


else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = tools.logout)
