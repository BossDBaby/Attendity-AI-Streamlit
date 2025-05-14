import bcrypt

# Function to hash a password
def generate_hashed_password(plain_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Rehash the password 'admin123'
hashed_admin_password = generate_hashed_password("student123")
print(f"Hashed password for admin123: {hashed_admin_password}")