

# database work is all here 


import sqlite3
from datetime import datetime

DB_NAME = "monitor.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # clients
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)

    # monitored urls
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitored_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            interval_sec INTEGER NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL,
            UNIQUE(client_id, url),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    # latest status (summary)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS url_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_id INTEGER UNIQUE NOT NULL,
            status_code INTEGER,
            response_time_ms REAL,
            error TEXT,
            checked_at TIMESTAMP,
            FOREIGN KEY (url_id) REFERENCES monitored_urls(id)
        )
    """)

    # error evidence
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url_id INTEGER NOT NULL,
            status_code INTEGER,
            status_type TEXT NOT NULL,
            occurred_at TIMESTAMP NOT NULL,
            FOREIGN KEY (url_id) REFERENCES monitored_urls(id)
        )
    """)

    conn.commit()
    conn.close()


# ---- client ops ----
def add_client(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO clients (name, created_at) VALUES (?, ?)",
            (name, datetime.utcnow())
        )
        conn.commit()
        print(f"Added client: {name}")
    except sqlite3.IntegrityError:
        print(f"Client already exists: {name}")
    finally:
        conn.close()


def get_client_id(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clients WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


# ---- url ops ----
def add_monitored_url(client_id: int, url: str, interval_sec: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO monitored_urls
            (client_id, url, interval_sec, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (client_id, url, interval_sec, datetime.utcnow())
        )
        conn.commit()
        print(f"Added URL: {url}")
    except sqlite3.IntegrityError:
        print(f"URL already exists for this client: {url}")
    finally:
        conn.close()


def get_active_urls():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, url, interval_sec
        FROM monitored_urls
        WHERE is_active = 1
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ---- status ops ----
def upsert_url_status(url_id, status_code, response_time_ms, error):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO url_status (url_id, status_code, response_time_ms, error, checked_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(url_id) DO UPDATE SET
            status_code = excluded.status_code,
            response_time_ms = excluded.response_time_ms,
            error = excluded.error,
            checked_at = excluded.checked_at
        """,
        (url_id, status_code, response_time_ms, error, datetime.utcnow())
    )
    conn.commit()
    conn.close()


def insert_error_event(url_id, status_code, status_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO error_events
        (url_id, status_code, status_type, occurred_at)
        VALUES (?, ?, ?, ?)
        """,
        (url_id, status_code, status_type, datetime.utcnow())
    )
    conn.commit()
    conn.close()
