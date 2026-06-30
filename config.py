import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATABASE_PATH = os.getenv("DATABASE_PATH", "jobs.db")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))

# HTTP-Verhalten der Module. Auf gedrosselten Umgebungen (z.B. GitHub-Runner-IPs)
# können einzelne .bund.de-Portale langsam sein -> Timeout/Retries hier justierbar.
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "15"))
HTTP_RETRIES = int(os.getenv("HTTP_RETRIES", "2"))
SERVICE_BUND_SEARCH_URL = os.getenv("SERVICE_BUND_SEARCH_URL")
BUNDESPOLIZEI_SEARCH_URL = os.getenv("BUNDESPOLIZEI_SEARCH_URL")
BKA_SEARCH_URL = os.getenv("BKA_SEARCH_URL")

# Interamt API
INTERAMT_API_KEYS = [k.strip() for k in os.getenv("INTERAMT_API_KEYS", "").split(",") if k.strip()]
INTERAMT_BASE_URL = os.getenv("INTERAMT_BASE_URL", "https://gate.interamt.de/interamtApi/v1/api")


# Bundesagentur für Arbeit (Jobsuche-API)
ARBEITSAGENTUR_UMKREIS = int(os.getenv("ARBEITSAGENTUR_UMKREIS", "0"))
ARBEITSAGENTUR_NUR_OEFFENTLICH = os.getenv("ARBEITSAGENTUR_NUR_OEFFENTLICH", "true").lower() == "true"

def validate_config():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("WARNUNG: TELEGRAM_BOT_TOKEN oder TELEGRAM_CHAT_ID fehlen in der .env Datei.")
        return False
    return True
