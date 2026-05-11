import feedparser
from base_module import BaseModule
import os

class BKAModule(BaseModule):
    @property
    def name(self):
        return "BKA"

    def fetch_jobs(self):
        url = os.getenv("BKA_SEARCH_URL")
        if not url:
            print("WARNUNG: BKA_SEARCH_URL nicht in .env definiert.")
            return []

        # RSS View erzwingen
        rss_url = url
        if "view=renderRSS" not in rss_url:
            if "?" in rss_url:
                rss_url += "&view=renderRSS"
            else:
                rss_url += "?view=renderRSS"

        # Optimierung: Erst mit requests holen (schnellerer Timeout & Handling)
        try:
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(rss_url, timeout=10, headers=headers)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        except Exception as e:
            print(f"Fehler beim Laden des BKA-Feeds: {e}")
            return []

        jobs = []
        for entry in feed.entries:
            # ID aus dem Link extrahieren (z.B. .../T-2026-31.html -> T-2026-31)
            job_id = entry.link.split('/')[-1].replace('.html', '')
            
            jobs.append({
                'id': job_id,
                'title': entry.title,
                'url': entry.link
            })
        
        return jobs
