import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATABASE_PATH = os.getenv("DATABASE_PATH", "jobs.db")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))
SERVICE_BUND_SEARCH_URL = os.getenv("SERVICE_BUND_SEARCH_URL")
BUNDESPOLIZEI_SEARCH_URL = os.getenv("BUNDESPOLIZEI_SEARCH_URL")
BKA_SEARCH_URL = os.getenv("BKA_SEARCH_URL")

def validate_config():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("WARNUNG: TELEGRAM_BOT_TOKEN oder TELEGRAM_CHAT_ID fehlen in der .env Datei.")
        return False
    return True
