from abc import ABC, abstractmethod
import re
import time
import requests
import feedparser
from config import HTTP_TIMEOUT, HTTP_RETRIES

DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
}


class BaseModule(ABC):
    DEFAULT_TIMEOUT = HTTP_TIMEOUT

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

    def get(self, url, retries=HTTP_RETRIES, **kwargs):
        """
        GET-Request über die geteilte Session inkl. Timeout & raise_for_status.
        Bei transienten Netzwerkfehlern (Connection-Reset, Timeout) wird erneut versucht.
        """
        kwargs.setdefault('timeout', self.DEFAULT_TIMEOUT)
        for attempt in range(retries + 1):
            try:
                response = self.session.get(url, **kwargs)
                response.raise_for_status()
                return response
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt >= retries:
                    raise
                time.sleep(1.5 * (attempt + 1))

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


# (m/w/d), (w/m/d), (m/w/d/i), m/w/d usw. inkl. umschließender Klammern entfernen
_GENDER_RE = re.compile(r"\(?\s*[mwd](?:\s*/\s*[mwdi]){1,3}\s*\)?", re.IGNORECASE)
_NONWORD_RE = re.compile(r"[^a-z0-9äöüß]+")


def normalize_for_dedup(title, location=""):
    """Normalisiert Titel (+optional Ort) zu einem quellenübergreifenden Dedup-Schlüssel."""
    text = f"{title or ''} {location or ''}".lower()
    text = _GENDER_RE.sub(" ", text)
    text = _NONWORD_RE.sub(" ", text)
    return " ".join(text.split())


# Behörden-Kennziffern wie AS-2026-072, AWV-2026-029, THW-2026-130, T-2026-29, UKRat-2026-008
_KENNZIFFER_RE = re.compile(r"\b([A-Za-z]{1,6}-\d{4}-\d{1,4})\b")


def extract_kennziffer(*texts):
    """
    Extrahiert eine Behörden-Kennziffer aus Titel/URL (falls vorhanden).
    Solche Kennziffern erscheinen oft in mehreren Quellen und eignen sich daher
    als robuster quellenübergreifender Dedup-Schlüssel.
    """
    for text in texts:
        m = _KENNZIFFER_RE.search(text or "")
        if m:
            return m.group(1).lower()
    return None
