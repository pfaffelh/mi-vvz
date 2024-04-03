import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import datetime 
import pymongo
import pandas as pd
from itertools import chain

# Seiten-Layout
st.set_page_config(page_title="VVZ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
from misc.util import *
import misc.tools as tools

# make all neccesary variables available to session_state
setup_session_state()

# Ab hier wird die Seite angezeigt
placeholder = st.empty()
with placeholder.form("login"):
    st.markdown("#### Login")
    kennung = st.text_input("Benutzerkennung")
    password = st.text_input("Passwort", type="password")
    submit = st.form_submit_button("Login")
    st.session_state.user = kennung
        
if submit and authenticate2(kennung, password) and can_edit(st.session_state.user):
    # If the form is submitted and the email and password are correct,
    # clear the form/container and display a success message
    placeholder.empty()
    st.session_state.logged_in = True
    st.success("Login successful")
    st.switch_page("VVZ")
elif submit:
    st.rerun()
else:
    pass

