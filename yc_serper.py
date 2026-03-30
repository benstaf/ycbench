import pandas as pd
import requests
import time
from urllib.parse import urlparse


df = pd.read_csv("yc_w26_startups.csv")

def domain(url):
    return urlparse(url).netloc.replace("www.", "")

# Just test with the first domain
row = df.iloc[0]
d = domain(row["website"])

print(f"Testing with domain: {d}")

r = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
    json={"q": d, "num": 1},
    timeout=10
)

print("HTTP status:", r.status_code)
print("Full response:")
print(r.text)
