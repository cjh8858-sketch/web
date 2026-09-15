import sqlite3
from pathlib import Path
from config import Config

def get_db_connection():
    """Get SQLite connection with row factory"""
    conn = sqlite3.connect(str(Config.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    Config.ensure_dirs()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Settings table for API keys and blog ID
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Interests table for keywords to track
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL UNIQUE,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Schedules table for daily post generation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interest_id INTEGER NOT NULL UNIQUE,
            run_hour INTEGER NOT NULL,
            run_minute INTEGER NOT NULL,
            enabled INTEGER DEFAULT 1,
            last_run_at TEXT,
            FOREIGN KEY (interest_id) REFERENCES interests(id)
        )
    """)

    # Publish history for tracking generated and published posts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publish_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interest_id INTEGER,
            keyword TEXT,
            title TEXT,
            naver_post_url TEXT,
            status TEXT,
            error_message TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (interest_id) REFERENCES interests(id)
        )
    """)

    # Naver session metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS naver_session_meta (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            saved_at TEXT,
            is_valid INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully")

if __name__ == "__main__":
    init_db()
