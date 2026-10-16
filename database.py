import os, sqlite3, json
from pathlib import Path
from config import APP_NAME, DB_PATH


def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            class_name TEXT,
            face_descriptors TEXT DEFAULT '[]',
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            available_qty INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrowed_at TEXT,
            due_at TEXT,
            returned_at TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            student_name TEXT,
            book_name TEXT,
            details TEXT,
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    conn.commit()
    conn.close()

    # Seed demo data if empty
    conn = get_db_connection()
    if conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
        conn.execute(
            "INSERT INTO books (code, title, available_qty, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("SACH001", "Dế Mèn phiêu lưu ký", 3, __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'), __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        )
    if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        conn.execute(
            "INSERT INTO students (name, class_name, face_descriptors, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("Nguyễn Văn A", "10A1", "[]", __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'), __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        )
    conn.commit(); conn.close()


def ensure_user_schema():
    # Compatibility function for application startup.
    return True
