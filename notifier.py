import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class Notifier:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_notification(self, message):
        if not self.token or not self.chat_id:
            print(f"Versand fehlgeschlagen (Konfiguration fehlt): {message}")
            return

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Fehler beim Senden der Telegram-Nachricht: {e}")

    def notify_job(self, portal, title, url):
        message = (
            f"<b>Neuer Treffer auf {portal}</b>\n\n"
            f"📌 {title}\n"
            f"🔗 <a href='{url}'>Direkt zum Angebot</a>"
        )
        self.send_notification(message)

    def notify_jobs_bundled(self, new_jobs):
        """new_jobs: Liste von (portal_name, job_dict)"""
        if not new_jobs:
            return

        # Gruppieren nach Portal
        grouped_jobs = {}
        for portal, job in new_jobs:
            if portal not in grouped_jobs:
                grouped_jobs[portal] = []
            grouped_jobs[portal].append(job)

        # Reihenfolge: Bund-Quellen zuerst, "Land Berlin" als Zusatz zuletzt
        ordered_portals = sorted(grouped_jobs, key=lambda p: (p == "Land Berlin", p))

        header = f"🔔 <b>{len(new_jobs)} neue Stellen gefunden!</b>\n\n"
        message = header

        for portal in ordered_portals:
            jobs = grouped_jobs[portal]
            portal_section = f"<b>🏢 {portal}</b>\n" + "─" * 15 + "\n"
            
            if len(message) + len(portal_section) > 4000:
                self.send_notification(message)
                message = header + portal_section
            else:
                message += portal_section

            for job in jobs:
                job_entry = f"📍 <b>{job['title']}</b>\n🔗 <a href='{job['url']}'>Ansehen</a>\n\n"
                
                if len(message) + len(job_entry) > 4000:
                    self.send_notification(message)
                    message = header + job_entry
                else:
                    message += job_entry

        self.send_notification(message)
