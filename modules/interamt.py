from base_module import BaseModule
from config import INTERAMT_API_KEYS, INTERAMT_BASE_URL

# Neue Konfiguration für Filter (optional)
import os
INTERAMT_FILTER_KEYWORDS = [k.strip().lower() for k in os.getenv("INTERAMT_FILTER_KEYWORDS", "").split(",") if k.strip()]
INTERAMT_FILTER_LOCATION = os.getenv("INTERAMT_FILTER_LOCATION", "").strip().lower()

class InteramtModule(BaseModule):
    @property
    def name(self):
        return "interamt.de"

    def fetch_jobs(self):
        if not INTERAMT_API_KEYS:
            print("WARNUNG: INTERAMT_API_KEYS nicht in .env definiert.")
            return []

        all_jobs = []
        url = f"{INTERAMT_BASE_URL}/Stellenangebote"
        
        for api_key in INTERAMT_API_KEYS:
            headers = {
                "X-API-Key": api_key,
                "Accept": "application/json"
            }

            try:
                key_preview = api_key[:8] + "..."
                print(f"  Abfrage Mandant (Key: {key_preview})...", end=" ", flush=True)

                response = self.get(url, headers=headers)
                data = response.json()
                
                raw_jobs = data.get("stellenangebote", [])
                
                filtered_count = 0
                for item in raw_jobs:
                    job_id = str(item.get("Id"))
                    kerndaten = item.get("Kerndaten", {})
                    title = kerndaten.get("Stellenbezeichnung", "Unbekannter Titel")
                    
                    # Filtering
                    title_lower = title.lower()
                    
                    # Ort extrahieren (Liste von EinsatzOrt Objekten)
                    einsatzorte = kerndaten.get("EinsatzOrt", [])
                    orte_str = " ".join([o.get("EinsatzOrt", "").lower() for o in einsatzorte])
                    
                    
                    # Keyword Filter
                    if INTERAMT_FILTER_KEYWORDS:
                        if not any(kw in title_lower for kw in INTERAMT_FILTER_KEYWORDS):
                            continue
                    
                    # Location Filter
                    if INTERAMT_FILTER_LOCATION:
                        if INTERAMT_FILTER_LOCATION not in orte_str:
                            continue
                    
                    job_url = f"https://www.interamt.de/koop/app/stelle?id={job_id}"
                    
                    all_jobs.append({
                        'id': job_id,
                        'title': title,
                        'url': job_url
                    })
                    filtered_count += 1
                
                print(f"gefunden: {len(raw_jobs)} (gefiltert: {filtered_count})")
                
            except Exception as e:
                print(f"Fehler bei Mandant {api_key[:8]}: {e}")
            
        return all_jobs
