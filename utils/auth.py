import json
import os
import bcrypt

# Path to users JSON file
USERS_FILE = "data/users.json"

# Load users from JSON
def load_users():
    if not os.path.exists(USERS_FILE):
        # If the users file does not exist, create it with an empty dictionary
        save_users({})
        return {}

    with open(USERS_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            # If JSON decoding fails, return an empty dictionary and log an error
            print("Error decoding the JSON file. Returning an empty user list.")
            return {}

# Save users to JSON (for admin use or registration feature)
def save_users(users):
    # Ensure the directory exists before saving
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Hashing function for password storage using bcrypt
def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Login validation
def login_user(username, password, users):
    if username in users:
        hashed_password = users[username]["password"].encode('utf-8')
        print(f"Hash stored: {hashed_password}")  # Debugging print
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True
        else:
            print(f"Hash comparison failed for {username}")  # Debugging print
    return False

# Add user (admin feature)
def add_user(username, password, role="student"):
    users = load_users()
    if username in users:
        return False  # user already exists
    users[username] = {
        "password": hash_password(password),
        "role": role
    }
    save_users(users)
    return True
