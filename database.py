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
            # Quellenübergreifende Deduplizierung: Spalte ergänzen, falls noch nicht vorhanden
            existing = {row[1] for row in self.conn.execute("PRAGMA table_info(jobs)")}
            if "dedup_key" not in existing:
                self.conn.execute("ALTER TABLE jobs ADD COLUMN dedup_key TEXT")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_dedup ON jobs (dedup_key)")

    def job_exists(self, job_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
        return cursor.fetchone() is not None

    def dedup_key_exists(self, dedup_key):
        """Prüft, ob bereits eine (ggf. quellenfremde) Stelle mit gleichem Dedup-Key bekannt ist."""
        if not dedup_key:
            return False
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM jobs WHERE dedup_key = ?", (dedup_key,))
        return cursor.fetchone() is not None

    def add_job(self, job_id, portal, title, url, dedup_key=None):
        with self.conn:
            self.conn.execute(
                "INSERT INTO jobs (job_id, portal, title, url, dedup_key) VALUES (?, ?, ?, ?, ?)",
                (job_id, portal, title, url, dedup_key)
            )

    def close(self):
        self.conn.close()
