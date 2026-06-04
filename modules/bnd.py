from urllib.parse import urljoin
from bs4 import BeautifulSoup
from base_module import BaseModule
from config import FILTER_LOCATION_KEYWORDS

BASE_URL = "https://www.bnd.bund.de"
SEARCH_URL = "https://www.bnd.bund.de/SiteGlobals/Forms/Suche/erweiterte_Karrieresuche_Formular.html"

# IT-Bezug im Titel oder in den Berufsfeld-"Bubbles" erkennen. Bewusst ohne nacktes "it",
# da das als Substring z.B. in "Mitarbeiter" matchen würde -> stattdessen "it-".
IT_KEYWORDS = [
    "it-", "informatik", "software", "daten", "data", "netzwerk", "cyber",
    "digital", "sap", "programmier", "krypto", "rechenzentrum", "operations",
    "kommunikationssystem", "intelligence", "system", "iuk", "administration",
]


class BNDModule(BaseModule):
    @property
    def name(self):
        return "BND"

    def fetch_jobs(self):
        try:
            response = self.get(SEARCH_URL)
        except Exception as e:
            print(f"Fehler beim Laden des BND-Karriereportals: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        seen = set()

        for link in soup.select('a.c-career-item__link'):
            href = link.get('href', '')
            if not href or href in seen:
                continue
            seen.add(href)

            # Saubere Stellenbezeichnung aus dem Titel-Element (ohne Berufsfeld-Tags)
            title_tag = link.select_one('.c-career-item__title')
            title = " ".join((title_tag or link).get_text().split()).replace("\xad", "")
            if not title:
                continue

            # Bubbles tragen Ort, Berufsfeld und Qualifikation -> für die Filterung nutzen
            bubbles = " ".join(b.get_text(" ", strip=True) for b in link.select('.c-bubble'))

            # Standort Berlin UND IT-Bezug verlangen (clientseitig, da kein Server-Filter)
            if not self.matches_filters(
                f"{title} {bubbles}", keywords=IT_KEYWORDS, locations=FILTER_LOCATION_KEYWORDS
            ):
                continue

            job_url = urljoin(BASE_URL + '/', href).split('?')[0]
            job_id = job_url.rstrip('/').split('/')[-1].replace('.html', '')

            jobs.append({
                'id': job_id,
                'title': title,
                'url': job_url
            })

        return jobs
