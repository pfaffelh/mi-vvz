import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
from misc.config import *
from misc.util import *

# Wird benötigt, falls ein Gebäude gelöscht wird, das noch Orte hat.
gebaeude_leer = gebaeude.find_one({"name_de": "-"})

def delete_confirm_one(x):
    y = list(ort.find({"gebaeude": x["_id"]}))
    s = ""
    for z in y:
        z_updated = {"gebaeude": gebaeude_leer["_id"]}
        ort.update_one(z, {"$set": z_updated })
        s = f"{s}  \n{z['name_de']}"
    if s != "":
        if len(y) == 1:
            s = s +  "  \nhat nun kein Gebäude mehr."
        else:
            s = s +  "  \nhaben nun kein Gebäude mehr."
    gebaeude.delete_one(x)
    reset()
    st.success(f"Erfolgreich gelöscht! {s}")

def update_confirm(x, x_updated):
    gebaeude.update_one(x, {"$set": x_updated })
    reset()
    st.success("Erfolgreich geändert!")

# Ändert die Reihenfolge der Darstellung
def move_up(x):
    target = gebaeude.find_one({"rang": {"$lt": x["rang"]}}, sort = [("rang",pymongo.DESCENDING)])
    if target:
        n= target["rang"]
        gebaeude.update_one(target, {"$set": {"rang": x["rang"]}})    
        gebaeude.update_one(x, {"$set": {"rang": n}})    
def move_down(x):
    target = gebaeude.find_one({"rang": {"$gt": x["rang"]}}, sort = [("rang", pymongo.ASCENDING)])
    if target:
        n= target["rang"]
        gebaeude.update_one(target, {"$set": {"rang": x["rang"]}})    
        gebaeude.update_one(x, {"$set": {"rang": n}})    

# make all neccesary variables available to session_state
setup_session_state()

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

# Navigation in Sidebar anzeigen
display_navigation()

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:

  st.header("Gebäude")
  st.write("**Fettgrdruckte** Gebäude sind in Auswahlmenüs sichtbar.")
  st.write(" ")
  if st.button('**Neues Gebäude hinzufügen**'):
    z = gebaeude.find()
    rang = (sorted(z, key=lambda x: x['rang'])[0])["rang"]-1
    x = gebaeude.insert_one({"name_de": "neu", "name_en": "", "kurzname": "", "adresse": "", "url": "", "sichtbar": True, "kommentar": "", "rang": rang})
    st.session_state.expanded=x.inserted_id
    st.rerun()

  y = list(gebaeude.find(sort=[("rang", pymongo.ASCENDING)]))

  for x in y:
    co1, co2, co3 = st.columns([12,1,1]) 
    with co1:
        with st.expander(f"**{x['name_de']}**" if x["sichtbar"] else x["name_de"], (True if x["_id"] == st.session_state.expanded else False)):
            with st.form(f'ID-{x["_id"]}'):
                sichtbar = st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == gebaeude_leer["_id"] else False))
                name_de=st.text_input('Name (de)', x["name_de"], disabled = (True if x["_id"] == gebaeude_leer["_id"] else False))
                name_en=st.text_input('Name (en)', x["name_en"])
                kurzname=st.text_input('Kurzname', x["kurzname"])
                adresse=st.text_input('Adresse', x["adresse"])
                url=st.text_input('Url', x["url"])
                kommentar=st.text_area('Kommentar', x["kommentar"])
                x_updated = ({"name_de": name_de, "name_en": name_en, "kurzname": kurzname, "adresse": adresse, "url": url, "sichtbar": sichtbar, "kommentar": kommentar})
                col1, col2, col3 = st.columns([1,2,1]) 
                with col1: 
                    submit = st.form_submit_button('Speichern')
                if submit:
                    update_confirm(x, x_updated, )
                    time.sleep(2)
                    st.rerun()                      
                with col3: 
                    deleted = st.form_submit_button("Löschen", disabled = (True if x["_id"] == gebaeude_leer["_id"] else False))
                    if deleted:
                        st.session_state.submitted = True
                        st.session_state.expanded = x["_id"]
                        st.rerun()
                if st.session_state.submitted:
                    col1, col2, col3 = st.columns([1,2,1]) 
                    with col1: 
                        st.form_submit_button(label = "Ja", on_click = delete_confirm_one, args = (x,))        
                    with col2: 
                        y = list(ort.find({"gebaeude": x["_id"]}))
                        s = ""
                        for z in y:
                            s = f"{s}  \n{z['name_de']}"
                        if s != "":
                            if len(y) == 1:
                                s = s +  "  \nist noch in diesem Gebäude."
                            else:
                                s = s +  "  \nsind noch in diesem Gebäude."
                        st.warning("Eintrag wirklich löschen?" + s)
                    with col3: 
                        st.form_submit_button(label="Nein", on_click = reset, args=("Nicht gelöscht!",))
    with co2: 
        st.button('↓', key=f'down-{x["_id"]}', on_click = move_down, args = (x, ))
    with co3:
        st.button('↑', key=f'up-{x["_id"]}', on_click = move_up, args = (x, ))

    if submit:
        reset()
        st.rerun()

else: 
    switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
