from bs4 import BeautifulSoup
from base_module import BaseModule
from config import STRICT_HD_FILTER, FILTER_HD_KEYWORDS

BASE_URL = "https://karriere.bund.de"
SEARCH_URL = "https://karriere.bund.de/arbeiten-bei-uns/stellenangebote-bei-uns"


class KarriereBundModule(BaseModule):
    @property
    def name(self):
        return "karriere.bund.de"

    def fetch_jobs(self):
        # Solr-Suche: Freitext Informatik, Bundesland Berlin, nur reguläre Stellen
        params = [
            ('tx_solr[q]', 'Informatik'),
            ('tx_solr[filter][]', 'state:Berlin'),
            ('tx_solr[filter][entryLevelOptions]', 'entryLevelOptions:work'),
        ]

        try:
            response = self.get(SEARCH_URL, params=params)
        except Exception as e:
            print(f"Fehler beim Laden von karriere.bund.de: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        seen = set()

        # Jede Stelle ist eine Flip-Card (.card--job); Vorder-/Rückseite teilen denselben Link
        for card in soup.select('.card--job'):
            link = card.select_one('a[href]')
            if not link:
                continue

            href = link.get('href')
            if href in seen:
                continue
            seen.add(href)

            job_url = href if href.startswith('http') else BASE_URL + href
            job_id = href.rstrip('/').split('/')[-1]

            # Karten-Text bereinigen: "Titel  Arbeitgeber  Ort | Vollzeit"
            text = " ".join(card.get_text(" ", strip=True).split())
            for noise in ("Karte umdrehen", "jetzt lesen"):
                text = text.replace(noise, "")
            title = text.strip() or " ".join(link.get_text().split())

            if STRICT_HD_FILTER and not self.matches_filters(title, keywords=FILTER_HD_KEYWORDS):
                continue

            jobs.append({
                'id': job_id,
                'title': title,
                'url': job_url
            })

        return jobs
