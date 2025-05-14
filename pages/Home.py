import streamlit as st
import pandas as pd

# 🛠 Page config
st.set_page_config(page_title="Home - Attendity", layout="centered")

# 🔒 Authentication check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("You must be logged in to access this page.")
    st.sidebar.warning("You must log in to access the Dashboard.")
    
    if st.button("Go to Login"):
        st.switch_page("app.py")  # Immediate redirect

    st.stop()

# 🚪 Logout function
def logout():
    for key in ["logged_in", "username", "is_admin", "name"]:
        st.session_state.pop(key, None)
    st.success("You have been logged out.")
    st.switch_page("app.py")

# 🎛 Sidebar
st.sidebar.markdown("### Navigation")
if st.sidebar.button("🔓 Log Out"):
    logout()

# 🛠 Admin tools (only if admin)
if st.session_state.get("is_admin"):
    st.sidebar.divider()
    st.sidebar.markdown("### Admin Section")
    st.sidebar.button("Manage Users")  # Placeholder
    st.sidebar.button("Manage Schedule")  # Placeholder

# 👋 Welcome user
full_name = st.session_state.get("name", st.session_state.get("username", "User"))
st.title(f"Hi, {full_name} 👋")
st.subheader("Welcome to your Class Dashboard")

# 📅 Dummy class schedule
st.markdown("### 📘 Today's Schedule")
classes = pd.DataFrame({
    "Subject": ["UI/UX", "Project", "AI", "Cyber Security", "Ethical Hacking"],
    "Time": ["09:30 AM", "10:40 AM", "11:45 AM", "12:10 PM", "12:45 PM"]
})

# 📊 Show styled class table
st.dataframe(
    classes.style.applymap(lambda val: 'background-color: lightblue' if 'AI' in val else ''),
    use_container_width=True
)
