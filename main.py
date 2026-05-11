import time
import importlib
import pkgutil
from config import validate_config, CHECK_INTERVAL_MINUTES
from database import Database
from notifier import Notifier
from base_module import BaseModule
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

    while True:
        all_new_jobs = []
        for module in active_modules:
            print(f"Suche auf {module.name}...")
            try:
                jobs = module.fetch_jobs()
                for job in jobs:
                    if not db.job_exists(job['id']):
                        print(f"Neuer Job gefunden: {job['title']}")
                        db.add_job(job['id'], module.name, job['title'], job['url'])
                        all_new_jobs.append((module.name, job))
            except Exception as e:
                print(f"Fehler im Modul {module.name}: {e}")

        if all_new_jobs:
            notifier.notify_jobs_bundled(all_new_jobs)
        else:
            print("Keine neuen Jobs gefunden.")

        if not loop:
            break

        print(f"Warte {CHECK_INTERVAL_MINUTES} Minuten bis zur nächsten Suche...")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    # Wenn wir auf GitHub Actions laufen, wollen wir nur einen Durchlauf
    is_github = os.getenv("GITHUB_ACTIONS") == "true"
    run(loop=not is_github)
