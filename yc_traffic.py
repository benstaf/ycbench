import pandas as pd
import requests
import time
from urllib.parse import urlparse

INPUT_FILE = "yc_w26_startups.csv"
OUTPUT_FILE = "yc_w26_traffic.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.similarweb.com/",
    "Accept": "application/json"
}

def extract_domain(url):
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")

df = pd.read_csv(INPUT_FILE)

results = []

for _, row in df.iterrows():

    name = row["name"]
    website = row["website"]
    domain = extract_domain(website)

    url = f"https://data.similarweb.com/api/v1/data?domain={domain}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code == 200:
            data = r.json()
            visits = data.get("EstimatedMonthlyVisits", {})

            for month, v in visits.items():
                results.append({
                    "name": name,
                    "domain": domain,
                    "month": month,
                    "visits": v
                })

            print("OK:", domain)

        else:
            print("Failed:", domain, r.status_code)

    except Exception as e:
        print("Error:", domain, e)

    time.sleep(1)

out = pd.DataFrame(results)
out.to_csv(OUTPUT_FILE, index=False)

print("Saved:", OUTPUT_FILE)
