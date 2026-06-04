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

        # RSS aktivieren und genug Ergebnisse anfordern
        rss_url = self.append_param(SERVICE_BUND_SEARCH_URL, "jobsrss=true")
        rss_url = self.append_param(rss_url, "resultsPerPage=100")

        try:
            feed = self.fetch_rss(rss_url)
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
