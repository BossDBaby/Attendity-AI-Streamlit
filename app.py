import os
import sys
import subprocess
import warnings

def install_and_import(package, version=None, pip_name=None):
    """Install package if not found and import it"""
    import_name = pip_name or package
    try:
        return __import__(import_name)
    except ImportError:
        warnings.warn(f"{package} not found! Installing now...")
        pip_package = f"{package}=={version}" if version else package
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--ignore-installed",  # Force reinstall if needed
            pip_package
        ])
        return __import__(import_name)

# Install and verify SQLAlchemy first
sqlalchemy = install_and_import("sqlalchemy", "2.0.41")
install_and_import("greenlet", "2.0.2")

# Now import streamlit and other packages
import streamlit as st

# Rest of your original app.py code
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