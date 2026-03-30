import pandas as pd
import requests
import time
from urllib.parse import urlparse

SERPAPI_KEY = "apikey"

#df = pd.read_csv("yc_w26_startups.csv")

def domain(url):
    return urlparse(url).netloc.replace("www.", "")

results = []

d = 'usecrow.ai'
try:
        r = requests.get(
            "https://serpapi.com/search",
            params={
                "api_key": SERPAPI_KEY,
                "engine": "google",
                "q": f'"{d}"',
                "num": 10,
                "tbs": "cdr:1,cd_min:01/01/2026",  # from Jan 1 2026
                "no_cache": True
            },
            timeout=15
        )
        data = r.json()
        total = data.get("search_information", {}).get("total_results")
        print(f"{d}: {total}")
except Exception as e:
        print(f"Error for {d}: {e}")
        results.append({"domain": d, "google_mentions": None})

