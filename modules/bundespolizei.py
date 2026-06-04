from bs4 import BeautifulSoup
from base_module import BaseModule
import os


class BundespolizeiModule(BaseModule):
    @property
    def name(self):
        return "Bundespolizei"

    def fetch_jobs(self):
        # Basis-URL, falls keine spezifische Filter-URL konfiguriert ist
        url = os.getenv(
            "BUNDESPOLIZEI_SEARCH_URL",
            "https://www.komm-zur-bundespolizei.de/verstaerkung/stellenmarkt"
        )

        try:
            response = self.get(url)
        except Exception as e:
            print(f"Fehler beim Abrufen der Bundespolizei-Seite: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []

        # Die Job-Container sind 'a' Tags mit der Klasse 'blockline'
        for item in soup.select('a.blockline'):
            try:
                job_url = item.get('href')
                if not job_url.startswith('http'):
                    job_url = "https://www.komm-zur-bundespolizei.de" + job_url

                # ID extrahieren (letzter Teil der URL)
                job_id = job_url.split('/')[-1]

                # Titel (erster Span im Div) und Ort (zweiter Span) extrahieren
                title_tag = item.select_one('div span')
                title = title_tag.get_text(strip=True) if title_tag else "Unbekannter Titel"
                spans = item.select('span')
                location = spans[1].get_text(strip=True) if len(spans) > 1 else ""
                full_title = f"{title} ({location})" if location else title

                jobs.append({
                    'id': job_id,
                    'title': full_title,
                    'url': job_url
                })
            except Exception as e:
                print(f"Fehler beim Parsen eines Jobs der Bundespolizei: {e}")

        return jobs
