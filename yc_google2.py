import pandas as pd
import requests
import time
import re
from urllib.parse import urlparse

df = pd.read_csv("yc_w26_startups.csv")

def domain(url):
    return urlparse(url).netloc.replace("www.", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

results = []

for _, row in df.iterrows():

    d = domain(row["website"])
    q = f'"{d}"'
    url = f"https://www.google.com/search?q={q}"

    print(f"\nChecking {d}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        print("HTTP status:", r.status_code)

        # show first part of HTML for debugging
        snippet = r.text[:500]
        print("HTML snippet:", snippet.replace("\n", " ")[:200])

        m = re.search(r'About ([0-9,]+) results', r.text)

        if m:
            count = int(m.group(1).replace(",", ""))
            print("Google mentions:", count)
        else:
            count = None
            print("Result count not found")

        results.append({
            "domain": d,
            "google_mentions": count
        })

    except Exception as e:
        print("Error:", e)
        results.append({
            "domain": d,
            "google_mentions": None
        })

    time.sleep(3)

# Save results
df_out = pd.DataFrame(results)
df_out.to_csv("yc_mentions.csv", index=False)

print("\nSaved results to yc_mentions.csv")
