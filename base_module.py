from abc import ABC, abstractmethod
import re
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

    @staticmethod
    def matches_filters(title, location="", keywords=None, locations=None):
        """
        Clientseitiger Filter für Quellen ohne serverseitige Filterung.

        keywords:  mind. eines muss im Titel vorkommen (z.B. höherer Dienst / IT).
        locations: mind. eines muss in Titel oder Ort vorkommen (z.B. berlin).
        Leere/None-Listen bedeuten "kein Filter" für das jeweilige Kriterium.
        """
        title_l = (title or "").lower()
        haystack = f"{title_l} {(location or '').lower()}"

        if keywords:
            if not any(kw in title_l for kw in keywords):
                return False
        if locations:
            if not any(loc in haystack for loc in locations):
                return False
        return True


# (m/w/d), (w/m/d), (m/w/d/i), m/w/d usw. inkl. umschließender Klammern entfernen
_GENDER_RE = re.compile(r"\(?\s*[mwd](?:\s*/\s*[mwdi]){1,3}\s*\)?", re.IGNORECASE)
_NONWORD_RE = re.compile(r"[^a-z0-9äöüß]+")


def normalize_for_dedup(title, location=""):
    """Normalisiert Titel (+optional Ort) zu einem quellenübergreifenden Dedup-Schlüssel."""
    text = f"{title or ''} {location or ''}".lower()
    text = _GENDER_RE.sub(" ", text)
    text = _NONWORD_RE.sub(" ", text)
    return " ".join(text.split())
