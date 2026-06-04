from bs4 import BeautifulSoup
from base_module import BaseModule
import os

BKA_BASE_URL = "https://www.karriere.bka.de/"


class BKAModule(BaseModule):
    @property
    def name(self):
        return "BKA"

    def fetch_jobs(self):
        url = os.getenv("BKA_SEARCH_URL")
        if not url:
            print("WARNUNG: BKA_SEARCH_URL nicht in .env definiert.")
            return []

        # Hinweis: Der frühere RSS-Export (view=renderRSS) liefert nur noch HTML,
        # daher parsen wir die Trefferliste direkt aus der Suchseite.
        try:
            response = self.get(url)
        except Exception as e:
            print(f"Fehler beim Laden der BKA-Seite: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []

        # Jede Stelle steckt in einem Container '.c-joboffer' mit einem Detail-Link
        for offer in soup.select('.c-joboffer'):
            link = offer.select_one('a[href]')
            if not link:
                continue

            href = link.get('href')
            job_url = href if href.startswith('http') else BKA_BASE_URL + href.lstrip('/')

            # ID aus dem Link extrahieren (z.B. .../T-2026-29.html -> T-2026-29)
            job_id = href.split('/')[-1].replace('.html', '')

            headline = offer.select_one('.c-joboffer__headline') or link
            title = " ".join(headline.get_text().split())

            jobs.append({
                'id': job_id,
                'title': title,
                'url': job_url
            })

        return jobs
