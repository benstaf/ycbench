import pandas as pd
import requests
import time
from urllib.parse import urlparse

SERPAPI_KEY = "key" #serpapi key 


df = pd.read_csv("yc_w26_startups.csv")

def domain(url):
    return urlparse(url).netloc.replace("www.", "")

results = []

for _, row in df.iterrows():
    d = domain(row["website"])
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": f'"{d}"',
                "num": 10,
                "tbs": "cdr:1,cd_min:08/17/2025,cd_max:10/31/2025",
#                "tbs": "cdr:1,cd_min:01/01/2026",  # from Jan 1 2026
                "no_cache": True
            },
            timeout=15
        )
        data = r.json()
        total = data.get("search_information", {}).get("total_results")
        print(f"{d}: {total}")
        results.append({"domain": d, "google_mentions": total})
    except Exception as e:
        print(f"Error for {d}: {e}")
        results.append({"domain": d, "google_mentions": None})
    time.sleep(2)

pd.DataFrame(results).to_csv("yc_mentions_early.csv", index=False)
print("Done.")
