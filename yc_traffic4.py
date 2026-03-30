import pandas as pd
import time
import random
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

INPUT_FILE = "yc_w26_startups.csv"

df = pd.read_csv(INPUT_FILE)


def domain(url):
    return urlparse(url).netloc.replace("www.", "")


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )

    for _, row in df.iterrows():

        d = domain(row["website"])
        url = f"https://www.similarweb.com/website/{d}/"

        print("\n--------------------------------")
        print("Visiting:", d)
        print("--------------------------------")

        context = browser.new_context()
        page = context.new_page()

        def handle_response(response):

            req_url = response.url

            # print all API requests for debugging
            if "api" in req_url:
                print("API REQUEST:", req_url)

            # look for traffic endpoints
            if "traffic" in req_url or "visits" in req_url or "engagement" in req_url:

                try:
                    data = response.json()

                    print("\n===== TRAFFIC DATA FOUND =====")
                    print(req_url)
                    print(data)
                    print("================================\n")

                except:
                    pass

        page.on("response", handle_response)

        try:

            page.goto(url, wait_until="networkidle")

            print("PAGE TITLE:", page.title())
            print("CURRENT URL:", page.url)

            # wait for graph requests
            page.wait_for_timeout(5000)

        except Exception as e:
            print("Error loading page:", e)

        context.close()

        # rate limiting protection
        sleep_time = random.uniform(6, 9)
        print(f"Sleeping {sleep_time:.1f}s...\n")
        time.sleep(sleep_time)

    browser.close()
