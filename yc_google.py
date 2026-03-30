import pandas as pd
import requests
import time
import re
from urllib.parse import urlparse

df = pd.read_csv("yc_w26_startups.csv")

def domain(url):
    return urlparse(url).netloc.replace("www.","")

HEADERS = {
 "User-Agent":"Mozilla/5.0"
}

results = []

for _, row in df.iterrows():

    d = domain(row["website"])
    q = f'"{d}"'
    url = f"https://www.google.com/search?q={q}"

    print("Checking", d)

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        m = re.search(r'About ([0-9,]+) results', r.text)

        if m:
            count = int(m.group(1).replace(",",""))
        else:
            count = None

        results.append({
            "domain": d,
            "google_mentions": count
        })

    except:
        results.append({
            "domain": d,
            "google_mentions": None
        })

    time.sleep(3)

pd.DataFrame(results).to_csv("yc_mentions.csv", index=False)
