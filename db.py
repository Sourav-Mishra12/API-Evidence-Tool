import sqlite3
from datetime import datetime 

DB_NAME = "monitor.db"

def get_conn():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()


    # Table 1: monitored URLs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitored_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            interval_sec INTEGER NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL
        )
    """)

    # Table 2: latest URL status
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


    # Table 3 : Error events (only errors , no success)
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


def add_monitored_url(url:str , interval_sec : int):
    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO monitored_urls (url, interval_sec, is_active, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (url, interval_sec, 1, datetime.utcnow())
        )
        conn.commit()
        print(f"Added URL: {url}")

    except sqlite3.IntegrityError:
        print(f"URL already exists: {url}")

    finally:
        conn.close()



def get_active_urls():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id , url , interval_sec
        FROM monitored_urls
        WHERE is_Active = 1

        """
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def upsert_url_status(
    url_id: int,
    status_code: int | None,
    response_time_ms: float | None,
    error: str | None
):
    conn = get_conn()
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
        (
            url_id,
            status_code,
            response_time_ms,
            error,
            datetime.utcnow()
        )
    )

    conn.commit()
    conn.close()


def insert_error_event(
    url_id: int,
    status_code: int | None,
    status_type: str
):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO error_events (url_id, status_code, status_type, occurred_at)
        VALUES (?, ?, ?, ?)
        """,
        (url_id, status_code, status_type, datetime.utcnow())
    )

    conn.commit()
    conn.close()



if __name__ == "__main__":
    init_db()
    

    urls = get_active_urls()
    if urls :
        url_id, url , _ = urls[0]
        upsert_url_status(url_id,200,123.45,None)
        print("Status stored for :" , url)