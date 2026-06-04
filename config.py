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

# Interamt API
INTERAMT_API_KEYS = [k.strip() for k in os.getenv("INTERAMT_API_KEYS", "").split(",") if k.strip()]
INTERAMT_BASE_URL = os.getenv("INTERAMT_BASE_URL", "https://gate.interamt.de/interamtApi/v1/api")


def _csv(name, default=""):
    return [v.strip().lower() for v in os.getenv(name, default).split(",") if v.strip()]


# Generische clientseitige Filter (für Quellen ohne serverseitigen Laufbahn-/Ort-Filter)
FILTER_HD_KEYWORDS = _csv(
    "FILTER_HD_KEYWORDS",
    "höherer dienst,a13,a14,a15,e13,e14,e15,master,referent,referatsleit,wissenschaftlich",
)
FILTER_LOCATION_KEYWORDS = _csv("FILTER_LOCATION_KEYWORDS", "berlin")

# Strenger "höherer Dienst"-Filter: standardmäßig aus, da Bund+IT+Berlin bereits stark
# vorfiltert und viele HD-Stellen die Keywords nicht im Titel tragen (Recall vor Precision).
STRICT_HD_FILTER = os.getenv("STRICT_HD_FILTER", "false").lower() == "true"

# Bundesagentur für Arbeit (Jobsuche-API)
ARBEITSAGENTUR_UMKREIS = int(os.getenv("ARBEITSAGENTUR_UMKREIS", "0"))
ARBEITSAGENTUR_NUR_OEFFENTLICH = os.getenv("ARBEITSAGENTUR_NUR_OEFFENTLICH", "true").lower() == "true"

def validate_config():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("WARNUNG: TELEGRAM_BOT_TOKEN oder TELEGRAM_CHAT_ID fehlen in der .env Datei.")
        return False
    return True
