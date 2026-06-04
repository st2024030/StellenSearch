from abc import ABC, abstractmethod
import requests
import feedparser

DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
}


class BaseModule(ABC):
    DEFAULT_TIMEOUT = 15

    def __init__(self):
        self._session = None

    @property
    def session(self):
        """Wiederverwendbare HTTP-Session (Connection-Reuse) mit Standard-Headern."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(DEFAULT_HEADERS)
        return self._session

    @property
    @abstractmethod
    def name(self):
        """Name des Portals"""
        pass

    @abstractmethod
    def fetch_jobs(self):
        """
        Sollte eine Liste von Dictionaries zurückgeben:
        [
            {'id': '123', 'title': 'Job Titel', 'url': 'https://...'},
            ...
        ]
        """
        pass

    # --- Gemeinsame Helfer für die Module ---

    def get(self, url, **kwargs):
        """GET-Request über die geteilte Session inkl. Timeout & raise_for_status."""
        kwargs.setdefault('timeout', self.DEFAULT_TIMEOUT)
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response

    def fetch_rss(self, url):
        """Lädt eine URL und parst sie als RSS/Atom-Feed."""
        response = self.get(url)
        return feedparser.parse(response.content)

    @staticmethod
    def append_param(url, param):
        """Hängt einen Query-Parameter an, falls noch nicht vorhanden."""
        key = param.split('=')[0]
        if f"{key}=" in url:
            return url
        separator = '&' if '?' in url else '?'
        return f"{url}{separator}{param}"
