import streamlit as st
import os
import shutil
from sqlalchemy.exc import IntegrityError
from config.database import db_manager
from models.attendance_models import User, Major
from utils.auth import hash_password
from face_recognition_model import load_user_encoding, regenerate_all_encodings

st.set_page_config(page_title="Admin Panel - Attendity")

# 🔒 Protect the page
if not st.session_state.get("logged_in") or not st.session_state.get("is_admin"):
    st.switch_page("pages/Home.py")

# ==== SIDEBAR ====
st.sidebar.markdown("### Account")
st.sidebar.button("🔓 Log Out", on_click=lambda: [st.session_state.clear(), st.rerun()])
st.sidebar.page_link(label="Home 🏠", page="pages/Home.py")
st.sidebar.page_link(label="History 📊", page= "pages/History.py")
st.sidebar.page_link(label="Attendance 🧍", page= "pages/Attendance.py")
st.sidebar.divider()
st.sidebar.markdown("### Admin Section")
st.sidebar.page_link(label="Admin Panel 🛠", page="pages/Admin.py")
st.sidebar.page_link(label="Admin Attendance History 🛠", page="pages/Admin_Attendance_HIstory.py")

st.title("🛠 Admin Panel")

# === Helper Functions ===

def get_all_students(search_query=""):
    session = db_manager.get_session()
    try:
        query = session.query(User).filter(User.role == "student")
        if search_query:
            search = f"%{search_query.lower()}%"
            query = query.filter(
                (User.username.ilike(search)) | (User.name.ilike(search))
            )
        return query.order_by(User.username).all()
    finally:
        session.close()

def get_all_majors():
    session = db_manager.get_session()
    try:
        return session.query(Major).order_by(Major.name).all()
    finally:
        session.close()

def add_student(username, password, name, email, major_id=None):
    session = db_manager.get_session()
    try:
        user = User(
            username=username,
            password_hash=hash_password(password),
            name=name,
            email=email,
            role="student",
            major_id=major_id,
        )
        session.add(user)
        session.commit()
        return True, None
    except IntegrityError:
        session.rollback()
        return False, "Username already exists."
    finally:
        session.close()

def update_student(user_id, new_name, new_email, major_id=None):
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found."
        user.name = new_name
        user.email = new_email
        user.major_id = major_id
        session.commit()
        return True, None
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def delete_student(user_id, username):
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found."
        session.delete(user)
        session.commit()
        # Remove photos folder
        shutil.rmtree(f"assets/user_photos/{username}", ignore_errors=True)
        return True, None
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def add_major(name):
    session = db_manager.get_session()
    try:
        major = Major(name=name)
        session.add(major)
        session.commit()
        return True, None
    except IntegrityError:
        session.rollback()
        return False, "Major already exists."
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def update_major(major_id, new_name):
    session = db_manager.get_session()
    try:
        major = session.query(Major).filter(Major.id == major_id).first()
        if not major:
            return False, "Major not found."
        major.name = new_name
        session.commit()
        return True, None
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def delete_major(major_id):
    session = db_manager.get_session()
    try:
        major = session.query(Major).filter(Major.id == major_id).first()
        if not major:
            return False, "Major not found."
        session.delete(major)
        session.commit()
        return True, None
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

# === 🏷️ Major Management Section ===
st.subheader("🏷️ Manage Majors")

majors = get_all_majors()
major_names = [m.name for m in majors]

with st.form("add_major_form"):
    new_major_name = st.text_input("New Major Name")
    submitted = st.form_submit_button("Add Major")
    if submitted:
        if new_major_name.strip() == "":
            st.warning("Major name cannot be empty.")
        elif new_major_name.strip() in major_names:
            st.warning("Major already exists.")
        else:
            success, err = add_major(new_major_name.strip())
            if success:
                st.success(f"Added major '{new_major_name.strip()}'")
                st.rerun()
            else:
                st.error(f"Error: {err}")

for major in majors:
    with st.expander(f"Edit Major: {major.name}"):
        new_name = st.text_input("Name", value=major.name, key=f"edit_major_{major.id}")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Update", key=f"update_major_{major.id}"):
                success, err = update_major(major.id, new_name.strip())
                if success:
                    st.success("Major updated.")
                    st.rerun()
                else:
                    st.error(f"Error: {err}")
        with col2:
            if st.button("Delete", key=f"delete_major_{major.id}"):
                success, err = delete_major(major.id)
                if success:
                    st.success("Major deleted.")
                    st.rerun()
                else:
                    st.error(f"Error: {err}")

st.markdown("---")

# === 👤 Student Management ===
st.subheader("👤 Student List")

search_query = st.text_input("🔍 Search by username or name")
students = get_all_students(search_query)

page_size = 10
total_pages = (len(students) - 1) // page_size + 1 if students else 1
page = st.session_state.get("student_page", 0)

# Adjust page if out of range
if page >= total_pages:
    page = total_pages - 1
    st.session_state["student_page"] = page
if page < 0:
    page = 0
    st.session_state["student_page"] = page

start = page * page_size
end = start + page_size
students_to_show = students[start:end]

if not students_to_show:
    if search_query.strip() != "":
        st.warning(f"No students found matching '{search_query}'.")
    else:
        st.info("No students available.")
else:
    # Build a fresh map id->name for majors in case updated
    majors = get_all_majors()
    major_options = {m.id: m.name for m in majors}
    for user in students_to_show:
        with st.expander(f"👤 {user.name} ({user.username})"):
            st.write(f"📧 Email: {user.email}")

            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input(f"Update Name - {user.username}", value=user.name, key=f"name_{user.id}")
                new_email = st.text_input(f"Update Email - {user.username}", value=user.email, key=f"email_{user.id}")

                # Major selectbox - sync with updated majors list
                current_major_name = major_options.get(user.major_id, "")
                new_major_name = st.selectbox(
                    f"Major (optional) - {user.username}",
                    options=[""] + list(major_options.values()),
                    index=list(major_options.values()).index(current_major_name) if current_major_name else 0,
                    key=f"major_{user.id}"
                )
                new_major_id = None
                for id_, name in major_options.items():
                    if name == new_major_name:
                        new_major_id = id_
                        break

                if st.button("✅ Update Info", key=f"update_{user.id}"):
                    st.session_state[f"confirm_update_{user.id}"] = True

                if st.session_state.get(f"confirm_update_{user.id}", False):
                    if st.button(f"Confirm Update for {user.username}", key=f"confirm_update_btn_{user.id}"):
                        success, err = update_student(user.id, new_name, new_email, new_major_id)
                        if success:
                            st.success(f"{user.username} updated successfully.")
                            st.session_state.pop(f"confirm_update_{user.id}")
                            st.rerun()
                        else:
                            st.error(f"Error: {err}")

            with col2:
                if st.button("🗑️ Delete Student", key=f"delete_{user.id}"):
                    st.session_state[f"confirm_delete_{user.id}"] = True

                if st.session_state.get(f"confirm_delete_{user.id}", False):
                    if st.button(f"Confirm Delete {user.username}", key=f"confirm_delete_btn_{user.id}"):
                        success, err = delete_student(user.id, user.username)
                        if success:
                            st.success(f"{user.username} deleted successfully.")
                            st.session_state.pop(f"confirm_delete_{user.id}")
                            st.rerun()
                        else:
                            st.error(f"Error: {err}")

            # Photo Upload Section
            st.markdown("**📷 Manage Photos**")
            uploaded_files = st.file_uploader(
                f"Upload photos for {user.username} (multiple allowed)",
                accept_multiple_files=True,
                type=["png", "jpg", "jpeg"],
                key=f"photo_upload_{user.id}",
            )
            if uploaded_files:
                user_photo_dir = f"assets/user_photos/{user.username}"
                os.makedirs(user_photo_dir, exist_ok=True)
                for file in uploaded_files:
                    with open(os.path.join(user_photo_dir, file.name), "wb") as f:
                        f.write(file.getbuffer())
                st.success(f"Uploaded {len(uploaded_files)} photos.")
                st.rerun()

            # Show existing photos
            user_photo_dir = f"assets/user_photos/{user.username}"
            if os.path.exists(user_photo_dir):
                photos = os.listdir(user_photo_dir)
                if photos:
                    st.write("Existing photos:")
                    cols = st.columns(min(5, len(photos)))
                    for i, photo in enumerate(photos):
                        with cols[i % 5]:
                            st.image(os.path.join(user_photo_dir, photo), width=100)
                else:
                    st.info("No photos uploaded yet.")
            else:
                st.info("No photos uploaded yet.")

            if st.button("🔄 Regenerate Face Encoding", key=f"regen_encoding_{user.id}"):
                encoding = load_user_encoding(user.username)
                if encoding is not None:
                    st.success(f"Encoding regenerated for {user.username}.")
                else:
                    st.warning("No photos found or encoding failed.")

# Pagination controls
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⬅ Previous") and page > 0:
        st.session_state["student_page"] = page - 1
        st.rerun()
with col3:
    if st.button("Next ➡") and page < total_pages - 1:
        st.session_state["student_page"] = page + 1
        st.rerun()
with col2:
    st.write(f"Page {page + 1} of {total_pages}")

if st.button("🔄 Regenerate All Face Encodings"):
    with st.spinner("Regenerating all face encodings, please wait..."):
        count = regenerate_all_encodings()
    st.success(f"Regenerated face encodings for {count} users.")

st.markdown("---")

# === Add New Student Section ===
st.subheader("➕ Add New Student")
with st.form("add_student_form"):
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    new_name = st.text_input("Full Name")
    new_email = st.text_input("Email")
    majors = get_all_majors()
    major_names = [m.name for m in majors]
    major_choice = st.selectbox("Select Major (optional)", options=[""] + major_names)
    major_id = None
    for m in majors:
        if m.name == major_choice:
            major_id = m.id
            break
    submitted = st.form_submit_button("Add Student")
    if submitted:
        if not new_username or not new_password or not new_name:
            st.warning("Username, password, and full name are required.")
        else:
            success, err = add_student(new_username.strip(), new_password, new_name.strip(), new_email.strip(), major_id)
            if success:
                st.success(f"Student '{new_username}' added.")
                st.rerun()
            else:
                st.error(f"Error: {err}")
