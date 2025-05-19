import streamlit as st
import os
import json
from utils.auth import hash_password
from face_recognition_model import load_user_encoding
import shutil

st.set_page_config(page_title="Admin Panel - Attendity")

# 🔒 Protect the page
if not st.session_state.get("logged_in") or not st.session_state.get("is_admin"):
    st.switch_page("pages/Login.py")

# ==== SIDEBAR ====
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link("pages/Home.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/History.py", label="History", icon="📊")
st.sidebar.divider()
st.sidebar.markdown("### Admin Section")
st.sidebar.page_link("pages/Admin.py", label="Admin Panel", icon="🛠")

st.title("🛠 Admin Panel")

# === 🧠 Helper Functions ===
def load_users():
    if os.path.exists("data/users.json"):
        with open("data/users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("data/users.json", "w") as f:
        json.dump(users, f, indent=4)

def filter_students(students, query):
    query = query.lower().strip()
    return {
        k: v for k, v in students.items()
        if query in k.lower() or query in v.get("name", "").lower()
    }

def paginate_students(students, page, page_size=10):
    items = list(students.items())
    start = page * page_size
    end = start + page_size
    return items[start:end], len(items)

# === ➕ Add Student ===
st.subheader("➕ Add New Student")

with st.form("add_student_form"):
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    new_name = st.text_input("Full Name")
    new_email = st.text_input("Email")
    submitted = st.form_submit_button("Add Student")

    if submitted:
        if not all([new_username, new_password, new_name, new_email]):
            st.warning("Please fill out all fields.")
        else:
            users = load_users()
            if new_username in users:
                st.error("Username already exists.")
            else:
                users[new_username] = {
                    "password": hash_password(new_password),
                    "name": new_name,
                    "email": new_email,
                    "role": "student"
                }
                save_users(users)
                st.success(f"Student '{new_username}' added successfully.")

st.markdown("---")

# === 👤 Student Management ===
st.subheader("👤 Student List")

users = load_users()
search_query = st.text_input("🔍 Search by username or name")

filtered_users = filter_students(users, search_query)
page_size = 10
total_pages = (len(filtered_users) - 1) // page_size + 1 if filtered_users else 1
page = st.session_state.get("student_page", 0)

# Adjust page if out of range
if page >= total_pages:
    page = total_pages - 1
    st.session_state["student_page"] = page
if page < 0:
    page = 0
    st.session_state["student_page"] = page

students_to_show, total = paginate_students(filtered_users, page, page_size)

if not students_to_show:
    if search_query.strip() != "":
        st.warning(f"No students found matching '{search_query}'.")
    else:
        st.info("No students available.")
else:
    for username, info in students_to_show:
        if info.get("role") == "admin":
            continue  # Skip admins from student list
        with st.expander(f"👤 {info.get('name', 'N/A')} ({username})"):
            st.write(f"📧 Email: {info.get('email', 'N/A')}")
            col1, col2 = st.columns(2)

            with col1:
                new_name = st.text_input(f"Update Name - {username}", value=info.get('name', ''), key=f"name_{username}")
                new_email = st.text_input(f"Update Email - {username}", value=info.get('email', ''), key=f"email_{username}")
                if st.button("✅ Update Info", key=f"update_{username}"):
                    st.session_state[f"confirm_update_{username}"] = True

                if st.session_state.get(f"confirm_update_{username}", False):
                    if st.button(f"Confirm Update for {username}", key=f"confirm_update_btn_{username}"):
                        users[username]["name"] = new_name
                        users[username]["email"] = new_email
                        save_users(users)
                        st.success(f"{username} updated successfully.")
                        st.session_state.pop(f"confirm_update_{username}")
                        st.rerun()

            with col2:
                if st.button("🗑️ Delete Student", key=f"delete_{username}"):
                    st.session_state[f"confirm_delete_{username}"] = True

                if st.session_state.get(f"confirm_delete_{username}", False):
                    if st.button(f"Confirm Delete {username}", key=f"confirm_delete_btn_{username}"):
                        del users[username]
                        save_users(users)
                        shutil.rmtree(f"assets/user_photos/{username}", ignore_errors=True)
                        st.success(f"Deleted student {username}")
                        st.session_state.pop(f"confirm_delete_{username}")
                        st.rerun()

            # 📷 Upload Photo
            photo_file = st.file_uploader(f"Upload new face photo for {username}", type=["jpg", "png"], key=f"photo_{username}")
            if photo_file:
                photo_dir = os.path.join("assets/user_photos", username)
                os.makedirs(photo_dir, exist_ok=True)
                with open(os.path.join(photo_dir, photo_file.name), "wb") as f:
                    f.write(photo_file.read())
                st.success("Photo uploaded successfully.")

                if st.button("🔄 Regenerate Encoding", key=f"regen_{username}"):
                    encoding = load_user_encoding(username)
                    if encoding is not None:
                        st.success("Encoding updated successfully.")
                    else:
                        st.error("No valid face found in uploaded image.")

# Pagination controls
prev_col, next_col = st.columns(2)
with prev_col:
    if st.button("⬅️ Previous") and page > 0:
        st.session_state["student_page"] = page - 1
        st.rerun()
with next_col:
    if st.button("➡️ Next") and (page + 1) * page_size < len(filtered_users):
        st.session_state["student_page"] = page + 1
        st.rerun()
