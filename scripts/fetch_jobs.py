import httpx
import json
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "jobs.json")

def main():
    url = "https://remotive.com/api/remote-jobs"
    resp = httpx.get(url, timeout=30)
    data = resp.json().get("jobs", [])
    # Save only relevant fields (title, company, description, url)
    simplified = []
    for job in data:
        simplified.append({
            "title": job.get("title", ""),
            "company_name": job.get("company_name", ""),
            "description": job.get("description", ""),
            "url": job.get("url", "")
        })
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(simplified)} jobs to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
