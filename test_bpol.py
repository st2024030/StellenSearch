from modules.bundespolizei import BundespolizeiModule
from dotenv import load_dotenv
import os

load_dotenv()

def test():
    module = BundespolizeiModule()
    print(f"Teste Modul: {module.name}")
    jobs = module.fetch_jobs()
    print(f"Gefundene Jobs: {len(jobs)}")
    for job in jobs[:5]:
        print(f"- {job['title']} ({job['url']})")

if __name__ == "__main__":
    test()
