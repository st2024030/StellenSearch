from abc import ABC, abstractmethod

class BaseModule(ABC):
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
