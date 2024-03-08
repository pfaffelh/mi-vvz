import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
from misc.config import *
from misc.util import *

class Gebaeude:
  """Ein Gebäude"""
  def __init__(self, name_de="", name_en="", kurzname="", adresse="", url="", rang=0, sichtbar=True, kommentar=""):
    self.name_de = name_de
    self.name_en = name_en
    self.kurzname = kurzname
    self.adresse = adresse
    self.url = url
    self.rang = rang
    self.sichtbar = sichtbar
    self.kommentar = kommentar

    def delete(self, confirm = True):
        y = list(ort.find({"gebaeude": self["_id"]}))
        s = ""
        for z in y:
            z_updated = {"gebaeude": x_leer["_id"]}
            ort.update_one(z, {"$set": z_updated })
            s = f"{s}  \n{z['name_de']}"
        if s != "":
            if len(y) == 1:
                s = s +  "  \nhat nun kein Gebäude mehr."
            else:
                s = s +  "  \nhaben nun kein Gebäude mehr."
        gebaeude.delete_one(self)
        reset()
        if confirm:
            st.success(f"Erfolgreich gelöscht! {s}")
      
    def update(self, x_updated, confirm = True):
        gebaeude.update_one(x, {"$set": x_updated })
        reset()
        if confirm:
            st.success("Erfolgreich geändert!")

# make all neccesary variables available to session_state
setup_session_state()

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# Navigation in Sidebar anzeigen
display_navigation()

# Wird benötigt, falls ein Gebäude gelöscht wird, das noch Orte hat.
x_leer = gebaeude.find_one({"name_de": "-"})

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:

  st.header("Gebäude")

  def delete_confirm_one(x):
    y = list(ort.find({"gebaeude": x["_id"]}))
    s = ""
    for z in y:
      z_updated = {"gebaeude": x_leer["_id"]}
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

  if st.button('Neues Gebäude hinzufügen'):
    z = gebaeude.find()
    rang = (sorted(z, key=lambda x: x['rang'])[0])["rang"]-1
    x = gebaeude.insert_one({"name_de": "neu", "name_en": "", "kurzname": "", "addresse": "", "url": "", "sichtbar": True, "kommentar": "", "rang": rang})
    st.session_state.expanded=x.inserted_id
    st.rerun()

  y = list(gebaeude.find(sort=[("rang", pymongo.ASCENDING)]))

  for x in y:
    st.write(type(x))
    with st.expander(x["name_de"], (True if x["_id"] == st.session_state.expanded else False)):
      with st.form(f'ID-{x["_id"]}'):
        sichtbar = st.checkbox("In Auswahlmenüs sichtbar", x["sichtbar"], disabled = (True if x["_id"] == x_leer["_id"] else False))
        name_de=st.text_input('Name (de)', x["name_de"], disabled = (True if x["_id"] == x_leer["_id"] else False))
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
            deleted = st.form_submit_button("Löschen")
            if deleted:
                st.session_state.submitted = True
                st.session_state.expanded = x["_id"]
        if st.session_state.submitted:
            col1, col2, col3 = st.columns([1,2,1]) 
            with col1: 
              st.form_submit_button(label = "Ja", on_click = Gebaeude.delete, args = (x,))        
            with col2: 
              st.warning("Eintrag wirklich löschen?")
            with col3: 
              st.form_submit_button(label="Nein", on_click = reset, args=("Nicht gelöscht!",))
        col1, col2, col3 = st.columns([1,2,1]) 
        with col1: 
          st.form_submit_button('↓', on_click = move_down, args = (x, ))
        with col2:
          st.write("Position in der Liste")
        with col3:
          st.form_submit_button('↑', on_click = move_up, args = (x, ))

  if submit:
    st.rerun()

else: 
  switch_page("VVZ")

st.sidebar.button("logout", on_click = logout)
