# fetch_jobs.py
import httpx
import json
import os

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
OUTPUT_PATH = os.path.join(APP_DIR, "jobs.json")

def main():
    url = "https://remotive.com/api/remote-jobs"
    
    try:
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("jobs", [])
        
        simplified = [{
            "title": job.get("title", ""),
            "company_name": job.get("company_name", ""),
            "description": job.get("description", ""),
            "url": job.get("url", "")
        } for job in data]
        
        os.makedirs(APP_DIR, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(simplified, f, ensure_ascii=False, indent=2)
            
        print(f"Saved {len(simplified)} jobs to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error fetching jobs: {e}")

if __name__ == "__main__":
    main()
