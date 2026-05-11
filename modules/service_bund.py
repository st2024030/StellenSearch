import feedparser
from base_module import BaseModule
from config import SERVICE_BUND_SEARCH_URL

class ServiceBundModule(BaseModule):
    @property
    def name(self):
        return "service.bund.de"

    def fetch_jobs(self):
        if not SERVICE_BUND_SEARCH_URL:
            print("WARNUNG: SERVICE_BUND_SEARCH_URL nicht in .env definiert.")
            return []

        # Sicherstellen, dass RSS aktiviert ist
        rss_url = SERVICE_BUND_SEARCH_URL
        if "jobsrss=true" not in rss_url:
            if "?" in rss_url:
                rss_url += "&jobsrss=true"
            else:
                rss_url += "?jobsrss=true"

        # Sicherstellen, dass wir genug Ergebnisse bekommen
        if "resultsPerPage=" not in rss_url:
             rss_url += "&resultsPerPage=100"

        # Optimierung: Erst mit requests holen
        try:
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(rss_url, timeout=10, headers=headers)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        except Exception as e:
            print(f"Fehler beim Laden des ServiceBund-Feeds: {e}")
            return []

        jobs = []
        for entry in feed.entries:
            jobs.append({
                'id': entry.id if hasattr(entry, 'id') else entry.link,
                'title': entry.title,
                'url': entry.link
            })
        
        return jobs
