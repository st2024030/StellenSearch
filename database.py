import sqlite3
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    portal TEXT,
                    title TEXT,
                    url TEXT,
                    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def job_exists(self, job_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
        return cursor.fetchone() is not None

    def add_job(self, job_id, portal, title, url):
        with self.conn:
            self.conn.execute(
                "INSERT INTO jobs (job_id, portal, title, url) VALUES (?, ?, ?, ?)",
                (job_id, portal, title, url)
            )

    def close(self):
        self.conn.close()
