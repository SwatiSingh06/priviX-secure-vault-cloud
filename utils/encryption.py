import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

def load_key():
    # Try environment variable first (required for cloud deployment)
    key = os.getenv('FERNET_KEY')
    if key:
        return key.encode()
    # Fallback to local file for local development
    with open("secret.key", "rb") as f:
        return f.read()

key = load_key()
cipher = Fernet(key)


def encrypt_file(input_path, output_path):
    with open(input_path, 'rb') as file:
        data = file.read()

    encrypted_data = cipher.encrypt(data)

    with open(output_path, 'wb') as file:
        file.write(encrypted_data)


def decrypt_file(input_path, output_path):
    with open(input_path, 'rb') as file:
        encrypted_data = file.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    with open(output_path, 'wb') as file:
        file.write(decrypted_data)