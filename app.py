# ===== DEPENDENCY VERIFICATION =====
import os
import sys
import subprocess
import warnings

# List of required packages with versions
REQUIRED_PACKAGES = {
    'sqlalchemy': '2.0.41',
    'greenlet': '2.0.2',
    'streamlit_extras': '0.7.1',
    'keras': '2.15.0',
    'tensorflow': '2.15.0',
    'protobuf': '5.27.3',
    'dlib': '19.24.0',
    'opencv-python': '4.11.0.86',
    'face_recognition': '1.3.0'
}

def ensure_packages():
    for pkg, version in REQUIRED_PACKAGES.items():
        try:
            __import__(pkg)
        except ImportError:
            warnings.warn(f"{pkg} not found, installing now...")
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                f"{pkg}=={version}"
            ])

# Special handling for MTCNN
try:
    from mtcnn import MTCNN
except ImportError:
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "pip", 
        "install", 
        "git+https://github.com/ipazc/mtcnn.git"
    ])

# Verify critical packages before other imports
ensure_packages()
# ===== END DEPENDENCY VERIFICATION =====

import streamlit as st

st.set_page_config(page_title="Attendity", layout="centered")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "name" not in st.session_state:
    st.session_state.name = None

# 🔁 Route user to the appropriate page
if st.session_state.logged_in:
    if st.session_state.is_admin:
        st.switch_page("pages/Admin.py")
    else:
        st.switch_page("pages/Home.py")
else:
    st.switch_page("pages/Login.py")