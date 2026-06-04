from bs4 import BeautifulSoup
from base_module import BaseModule
from config import STRICT_HD_FILTER, FILTER_HD_KEYWORDS

BASE_URL = "https://www.karriereportal-stellen.berlin.de"
SEARCH_URL = "https://www.karriereportal-stellen.berlin.de/stellenangebote.html"

# Tätigkeitsfeld "IT-Berufe" (serverseitiger Filter des rexx-Portals)
IT_AUFGABENGEBIET_ID = "59"

# Praktika/Ausbildung sind kein höherer Dienst -> ausschließen
EXCLUDE_KEYWORDS = ("praktikum", "ausbildung", "studierende", "werkstudent", "trainee")


class BerlinKarriereModule(BaseModule):
    @property
    def name(self):
        return "Land Berlin"

    def fetch_jobs(self):
        jobs = []
        seen = set()

        # rexx liefert 20 Treffer pro Seite; über start paginieren
        for page in range(5):
            params = [
                ('filter[aufgabengebiet_id][]', IT_AUFGABENGEBIET_ID),
                ('start', str(page * 20)),
            ]
            try:
                response = self.get(SEARCH_URL, params=params)
            except Exception as e:
                print(f"Fehler beim Laden des Berlin-Karriereportals: {e}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            new_on_page = 0

            for tr in soup.select('table tr'):
                link = tr.select_one('a[href]')
                if not link:
                    continue
                href = link.get('href', '')
                # nur echte Detailseiten (Slug.html), nicht die Suchseite selbst
                if not href.endswith('.html') or 'stellenangebote.html' in href:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                new_on_page += 1

                job_url = href if href.startswith('http') else BASE_URL + '/' + href.lstrip('/')
                job_id = href.rstrip('/').split('/')[-1].replace('.html', '')

                cells = [" ".join(td.get_text(" ", strip=True).split()) for td in tr.select('td')]
                bezeichnung = " ".join(link.get_text().split()) or (cells[0] if cells else "")
                behoerde = cells[1] if len(cells) > 1 else ""
                title = f"{bezeichnung} – {behoerde}" if behoerde else bezeichnung

                low = bezeichnung.lower()
                if any(x in low for x in EXCLUDE_KEYWORDS):
                    continue
                if STRICT_HD_FILTER and not self.matches_filters(title, keywords=FILTER_HD_KEYWORDS):
                    continue

                jobs.append({
                    'id': job_id,
                    'title': title,
                    'url': job_url
                })

            if new_on_page == 0:
                break

        return jobs
