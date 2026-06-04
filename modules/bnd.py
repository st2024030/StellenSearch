import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from base_module import BaseModule
from config import FILTER_LOCATION_KEYWORDS

BASE_URL = "https://www.bnd.bund.de"
SEARCH_URL = "https://www.bnd.bund.de/SiteGlobals/Forms/Suche/erweiterte_Karrieresuche_Formular.html"

# Detail-Links folgen dem Muster .../Stellenangebote/...AS-JJJJ-NNN....html
JOB_LINK_RE = re.compile(r"/Stellenangebote?/.+\.html", re.IGNORECASE)

# IT-Bezug im (beschreibenden) Linktext erkennen. Bewusst ohne nacktes "it",
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

        for link in soup.select('a[href]'):
            href = link.get('href', '')
            if not JOB_LINK_RE.search(href):
                continue
            if href in seen:
                continue
            seen.add(href)

            # Soft-Hyphens / Zero-Width-Spaces aus dem Linktext entfernen
            title = " ".join(link.get_text().split()).replace("\xad", "").replace("​", "")
            if not title:
                continue

            # Standort Berlin UND IT-Bezug verlangen (clientseitig, da kein Server-Filter)
            if not self.matches_filters(title, keywords=IT_KEYWORDS, locations=FILTER_LOCATION_KEYWORDS):
                continue

            job_url = urljoin(BASE_URL + '/', href).split('?')[0]
            job_id = job_url.rstrip('/').split('/')[-1].replace('.html', '')

            jobs.append({
                'id': job_id,
                'title': title,
                'url': job_url
            })

        return jobs
