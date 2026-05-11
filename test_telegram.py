from notifier import Notifier
from dotenv import load_dotenv
import os

load_dotenv()

def test_telegram():
    notifier = Notifier()
    print("Sende Test-Nachricht...")
    notifier.send_notification("<b>Test-Nachricht vom StellenRobot</b>\n\nWenn du das liest, funktioniert die Verbindung!")
    print("Erledigt. Bitte prüfe dein Telegram.")

if __name__ == "__main__":
    test_telegram()
