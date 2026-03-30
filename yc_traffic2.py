import pandas as pd
from curl_cffi import requests
from urllib.parse import urlparse
import time

df = pd.read_csv("yc_w26_startups.csv")

def extract_domain(url):
    return urlparse(url).netloc.replace("www.", "")

for _, row in df.iterrows():

    domain = extract_domain(row["website"])
    url = f"https://data.similarweb.com/api/v1/data?domain={domain}"

    r = requests.get(url, impersonate="chrome110")

    print(domain, r.status_code)

    if r.status_code == 200:
        print(r.json())

    time.sleep(1)
