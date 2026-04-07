import os
import psycopg2
import psycopg2.extras
from psycopg2.errors import UniqueViolation
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT,
        email VARCHAR(255) UNIQUE,
        google_id VARCHAR(255) UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Files (
        id SERIAL PRIMARY KEY,
        owner_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SharedFiles (
        id SERIAL PRIMARY KEY,
        shared_with_user_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
        original_owner_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
        original_file_id INTEGER NOT NULL REFERENCES Files(id) ON DELETE CASCADE,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
        action TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def create_user(username, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (username, password_hash) VALUES (%s, %s) RETURNING id",
            (username, password_hash)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except UniqueViolation:
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(user) if user else None

def get_user_by_google_id(google_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE google_id = %s", (google_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(user) if user else None

def update_google_user_id(user_id, google_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET google_id = %s WHERE id = %s", (google_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def create_google_user(username, email, google_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (username, email, google_id, password_hash) VALUES (%s, %s, %s, NULL) RETURNING id",
            (username, email, google_id)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except UniqueViolation:
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(user) if user else None

def store_file_metadata(owner_id, filename, filepath, file_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Files (owner_id, filename, filepath, hash, created_at) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING id",
        (owner_id, filename, filepath, file_hash)
    )
    file_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return file_id

def get_user_files(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Files WHERE owner_id = %s ORDER BY id DESC", (user_id,))
    files = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return files

def get_shared_files(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
    SELECT sf.*, u.username as owner_name
    FROM SharedFiles sf
    JOIN Users u ON sf.original_owner_id = u.id
    WHERE sf.shared_with_user_id = %s
    ORDER BY sf.id DESC
    ''', (user_id,))
    files = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return files

def get_file_by_id(file_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Files WHERE id = %s", (file_id,))
    file_record = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(file_record) if file_record else None

def share_file_with_user(shared_with_user_id, original_owner_id, original_file_id, filename, filepath, file_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO SharedFiles (shared_with_user_id, original_owner_id, original_file_id, filename, filepath, hash, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    ''', (shared_with_user_id, original_owner_id, original_file_id, filename, filepath, file_hash))
    conn.commit()
    cursor.close()
    conn.close()

def remove_shared_access(shared_file_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM SharedFiles WHERE id = %s AND shared_with_user_id = %s",
        (shared_file_id, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_shared_file_by_id(shared_file_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM SharedFiles WHERE id = %s", (shared_file_id,))
    file_record = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(file_record) if file_record else None

def is_file_already_shared(original_file_id, shared_with_user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM SharedFiles WHERE original_file_id = %s AND shared_with_user_id = %s",
        (original_file_id, shared_with_user_id)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

def has_shared_access(shared_file_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM SharedFiles WHERE id = %s AND shared_with_user_id = %s",
        (shared_file_id, user_id)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

def get_recent_logs(user_id, limit=5):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM Logs WHERE user_id = %s ORDER BY id DESC LIMIT %s", (user_id, limit))
    logs = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return logs

def log_action(user_id, action):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Logs (user_id, action, timestamp) VALUES (%s, %s, CURRENT_TIMESTAMP)", (user_id, action))
    conn.commit()
    cursor.close()
    conn.close()

def delete_file(file_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Files WHERE id = %s AND owner_id = %s", (file_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
