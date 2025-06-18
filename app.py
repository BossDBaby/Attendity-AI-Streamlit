import os
import sys
import subprocess
import warnings

def ensure_package(package, version=None, install_cmd=None):
    try:
        __import__(package)
    except ImportError:
        warnings.warn(f"{package} not found! Installing now...")
        if not install_cmd:
            install_cmd = [sys.executable, "-m", "pip", "install", f"{package}=={version}"]
        subprocess.run(install_cmd, check=True)

# Verify SQLAlchemy and greenlet first
ensure_package("sqlalchemy", "2.0.41")
ensure_package("greenlet", "2.0.2")

# Verify MTCNN
ensure_package("mtcnn", install_cmd=[sys.executable, "-m", "pip", "install", "git+https://github.com/ipazc/mtcnn.git"])

# Now import streamlit and continue with your app
import streamlit as st

st.set_page_config(page_title="Attendity", layout="centered")

# Rest of your original app.py code...
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