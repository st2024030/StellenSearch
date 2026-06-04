from base_module import BaseModule
from config import (
    ARBEITSAGENTUR_UMKREIS,
    ARBEITSAGENTUR_NUR_OEFFENTLICH,
    FILTER_LOCATION_KEYWORDS,
)

API_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
API_KEY = "jobboerse-jobsuche"
DETAIL_URL = "https://www.arbeitsagentur.de/jobsuche/jobdetail/{}"

# Arbeitgeber-Keywords, die auf den öffentlichen Dienst (v.a. Bund) hindeuten.
# Die Bundesagentur-Jobbörse enthält überwiegend private Stellen -> dieser Filter
# ist hier der entscheidende, um auf öffentliche Arbeitgeber einzugrenzen.
OEFFENTLICH_KEYWORDS = [
    "bund", "bundes", "ministerium", "amt", "behörde", "bundesanstalt",
    "bundesagentur", "öffentlichen rechts", "anstalt des öffentlichen",
    "körperschaft", "land berlin", "senat", "bezirks", "rentenversicherung",
    "polizei", "zoll", "universität", "hochschule", "charité", "deutsche bundesbank",
]


class ArbeitsagenturModule(BaseModule):
    @property
    def name(self):
        return "Arbeitsagentur"

    def fetch_jobs(self):
        headers = {"X-API-Key": API_KEY}
        params = {
            "wo": "Berlin",
            "berufsfeld": "Informatik",
            "umkreis": ARBEITSAGENTUR_UMKREIS,
            "angebotsart": 1,  # 1 = Arbeit (kein Praktikum/Ausbildung)
            "size": 100,
            "page": 1,
        }

        try:
            response = self.get(API_URL, headers=headers, params=params)
            data = response.json()
        except Exception as e:
            print(f"Fehler beim Abrufen der Arbeitsagentur-API: {e}")
            return []

        jobs = []
        for item in data.get("ergebnisliste", []):
            refnr = item.get("referenznummer")
            if not refnr:
                continue

            title = item.get("stellenangebotsTitel", "Unbekannter Titel")
            firma = item.get("firma", "") or ""

            lokationen = item.get("stellenlokationen", [])
            ort = lokationen[0].get("adresse", {}).get("ort", "") if lokationen else ""

            # Standortfilter (API liefert i.d.R. nur Berlin, hier zur Sicherheit)
            if not self.matches_filters(title, f"{firma} {ort}", locations=FILTER_LOCATION_KEYWORDS):
                continue

            # Öffentlicher-Dienst-Filter (Bund-Priorität)
            if ARBEITSAGENTUR_NUR_OEFFENTLICH and not any(
                kw in firma.lower() for kw in OEFFENTLICH_KEYWORDS
            ):
                continue

            display = f"{title} – {firma}" if firma else title
            jobs.append({
                'id': str(refnr),
                'title': display,
                'url': DETAIL_URL.format(refnr),
                'arbeitgeber': firma,
                'location': ort,
            })

        return jobs
