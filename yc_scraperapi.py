import pandas as pd
import requests
import time
from urllib.parse import urlparse

SCRAPERAPI_KEY = "key"

df = pd.read_csv("yc_w26_startups.csv")

def domain(url):
    return urlparse(url).netloc.replace("www.", "")

results = []
for _, row in df.iterrows():
    d = domain(row["website"])
    try:
        r = requests.get(
            "https://api.scraperapi.com/structured/google/search",
            params={
                "api_key": SCRAPERAPI_KEY,
                "query": f'"{d}"',
                "num": 10,
                "tbs": "cdr:1,cd_min:01/01/2026",  # from Jan 1 2026
                "country": "us",
            },
            timeout=30
        )
        data = r.json()
        total = data.get("search_information", {}).get("total_results")
        print(f"{d}: {total}")
        results.append({"domain": d, "google_mentions": total})
    except Exception as e:
        print(f"Error for {d}: {e}")
        results.append({"domain": d, "google_mentions": None})
    time.sleep(2)

pd.DataFrame(results).to_csv("yc_mentions.csv", index=False)
print("Done.")
