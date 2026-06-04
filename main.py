import sys
import time
import os
import importlib
import pkgutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import validate_config, CHECK_INTERVAL_MINUTES

# Auf GitHub Actions (kein TTY) wird stdout sonst gepuffert -> Logs erscheinen erst am
# Ende und der Lauf wirkt wie eingefroren. Zeilenweises Flushen macht den Fortschritt sichtbar.
try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass
from database import Database
from notifier import Notifier
from base_module import BaseModule, normalize_for_dedup, extract_kennziffer
import modules

def load_modules():
    loaded_modules = []
    for loader, module_name, is_pkg in pkgutil.iter_modules(modules.__path__):
        full_module_name = f"modules.{module_name}"
        module = importlib.import_module(full_module_name)
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if (isinstance(attribute, type) and 
                issubclass(attribute, BaseModule) and 
                attribute is not BaseModule):
                loaded_modules.append(attribute())
    return loaded_modules

def fetch_module(module):
    """Ruft die Jobs eines Moduls ab. Läuft pro Modul in einem eigenen Thread."""
    start = time.time()
    try:
        jobs = module.fetch_jobs()
        return module, jobs, time.time() - start, None
    except Exception as e:
        return module, [], time.time() - start, e


def run(loop=False):
    if not validate_config():
        return

    db = Database()
    notifier = Notifier()
    active_modules = load_modules()

    if not active_modules:
        print("Keine aktiven Module gefunden.")
        return

    print(f"Robot gestartet mit {len(active_modules)} Modulen: {[m.name for m in active_modules]}")

    try:
        while True:
            start_run = time.time()
            all_new_jobs = []

            print(f"Starte Suche auf {len(active_modules)} Portalen (parallel)...")

            # Module parallel abfragen -> Gesamtdauer = langsamstes Modul statt Summe.
            # Ergebnisse werden verarbeitet, sobald ein Modul fertig ist (Live-Fortschritt).
            with ThreadPoolExecutor(max_workers=len(active_modules)) as executor:
                futures = [executor.submit(fetch_module, m) for m in active_modules]

                for future in as_completed(futures):
                    module, jobs, duration, error = future.result()
                    if error:
                        print(f"  {module.name}: FEHLER nach {duration:.2f}s: {error}")
                        continue

                    label = f"{len(jobs)} Jobs in {duration:.2f}s"
                    if not jobs:
                        label += "  [!] 0 Jobs - evtl. Filter/Selektor pruefen"
                    print(f"  {module.name}: {label}")

                    for job in jobs:
                        # Bevorzugt die Behörden-Kennziffer (z.B. AS-2026-072) als robusten
                        # quellenübergreifenden Schlüssel, sonst den normalisierten Titel.
                        dedup_key = (
                            extract_kennziffer(job['title'], job['url'])
                            or normalize_for_dedup(job['title'], job.get('location', ''))
                        )
                        # Bekannt, wenn Quellen-ID ODER (quellenübergreifend) der Schlüssel existiert
                        if db.job_exists(job['id']) or db.dedup_key_exists(dedup_key):
                            continue
                        print(f"  -> Neuer Job: {job['title']}")
                        db.add_job(job['id'], module.name, job['title'], job['url'], dedup_key)
                        all_new_jobs.append((module.name, job))

            if all_new_jobs:
                print(f"Sende {len(all_new_jobs)} neue Jobs an Telegram...")
                notifier.notify_jobs_bundled(all_new_jobs)
            else:
                print("Keine neuen Jobs gefunden.")

            total_duration = time.time() - start_run
            print(f"Durchlauf beendet. Gesamtdauer: {total_duration:.2f}s")

            if not loop:
                break

            print(f"Warte {CHECK_INTERVAL_MINUTES} Minuten bis zur nächsten Suche...")
            time.sleep(CHECK_INTERVAL_MINUTES * 60)
    finally:
        db.close()

if __name__ == "__main__":
    # Wenn wir auf GitHub Actions laufen, wollen wir nur einen Durchlauf
    is_github = os.getenv("GITHUB_ACTIONS") == "true"
    run(loop=not is_github)
