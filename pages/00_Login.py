import streamlit as st
import time
from streamlit_extras.switch_page_button import switch_page 
from misc.util_session_init import * # some things which only have to be run once

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
import misc.util as util
import misc.tools as tools

# make all neccesary variables available to session_state
util.setup_session_state()

# Ab hier wird die Seite angezeigt
st.header("VVZ Login")

placeholder = st.empty()
with placeholder.form("login"):
    kennung = st.text_input("Benutzerkennung")
    password = st.text_input("Passwort", type="password")
    submit = st.form_submit_button("Login")
    st.session_state.user = kennung

if submit:
    if tools.authenticate(kennung, password): 
        if tools.can_edit(kennung):
            st.write("11")
            # If the form is submitted and the email and password are correct,
            # clear the form/container and display a success message
            placeholder.empty()
            st.session_state.logged_in = True
            st.success("Login successful")
            util.logger.info(f"User {st.session_state.user} hat in sich erfolgreich eingeloggt.")
            switch_page("VVZ")
        else:
            st.write(st.session_state.user)
            st.write("12")
            st.error("Nicht genügend Rechte, um VVZ zu editieren.")
            u = util.user.find_one({"rz": kennung})
            faq_id = util.group.find_one({"name": "faq"})["_id"]
            st.write(faq_id)
            st.write(u["groups"])
            st.write(True if faq_id in u["groups"] else False)
            util.logger.info(f"User {kennung} hatte nicht gebügend Rechte, um sich einzuloggen.")
            time.sleep(20)
            st.rerun()
    else: 
        st.write("13")
        st.error("Login nicht korrekt.")
        util.logger.info(f"Ein falscher Anmeldeversuch.")
        time.sleep(2)
        st.rerun()


