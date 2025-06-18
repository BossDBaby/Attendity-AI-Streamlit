import streamlit as st

st.set_page_config(page_title="Attendity", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "name" not in st.session_state:
    st.session_state.name = None

if st.session_state.logged_in:
    if st.session_state.is_admin:
        st.switch_page("pages/Admin.py")
    else:
        st.switch_page("pages/Home.py")
else:
    st.switch_page("pages/Login.py")