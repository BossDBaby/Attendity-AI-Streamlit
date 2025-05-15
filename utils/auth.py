import json
import os
import bcrypt

USERS_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        save_users({})
        return {}
    with open(USERS_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("Error decoding the JSON file. Returning an empty user list.")
            return {}

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def login_user(username, password, users):
    if username in users:
        hashed_password = users[username]["password"].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True
    return False

def add_user(username, password, role="student"):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "role": role
    }
    save_users(users)
    return True
