import pandas as pd
from playwright.sync_api import sync_playwright
import json
from urllib.parse import urlparse

df = pd.read_csv("yc_w26_startups.csv")

def domain(url):
    return urlparse(url).netloc.replace("www.","")

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    def handle_response(response):
        if "similarweb.com/api" in response.url:
            try:
                data = response.json()
                print(data)
            except:
                pass

    page.on("response", handle_response)

    for _, row in df.iterrows():
        d = domain(row["website"])
        url = f"https://www.similarweb.com/website/{d}/"
        print("Visiting", d)
        page.goto(url)

    browser.close()
