import os
import json
import time
import requests
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = RAW_DIR / "tweets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Config
# --------------------------------------------------

BATCH_JSON_URL = "https://yc-oss.github.io/api/batches/winter-2026.json"
APIFY_API_KEY = "YOUR_APIFY_KEY"

SLEEP_BETWEEN_QUERIES = 2   # seconds between queries for the same startup
SLEEP_BETWEEN_STARTUPS = 5  # seconds between startups
MAX_RETRIES = 3

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def load_batch():
    r = requests.get(BATCH_JSON_URL)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    return df[["name", "slug", "website"]]


def scrape_tweets(query, retries=MAX_RETRIES):
    actor_url = "https://api.apify.com/v2/acts/apidojo~tweet-scraper/run-sync-get-dataset-items"
    payload = {
        "searchTerms": [query],
        "maxItems": 50,
        "lang": "en"
    }

    for attempt in range(retries):
        try:
            r = requests.post(
                actor_url,
                params={"token": APIFY_API_KEY},
                json=payload,
                timeout=120
            )

            if r.status_code == 429:
                wait = 2 ** attempt * 10  # 10s, 20s, 40s
                print(f"  Rate limited on '{query}', waiting {wait}s...")
                time.sleep(wait)
                continue

            r.raise_for_status()
            return r.json()

        except requests.exceptions.Timeout:
            print(f"  Timeout on attempt {attempt + 1} for '{query}'")
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed for '{query}': {e}")

        time.sleep(2 ** attempt * 5)  # 5s, 10s, 20s before retry

    print(f"  All {retries} attempts failed for '{query}', skipping.")
    return []


# --------------------------------------------------
# Main
# --------------------------------------------------

def run():
    df = load_batch()
    total = len(df)

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        name = row["name"]
        slug = row["slug"]
        website = row["website"]

        output_path = OUTPUT_DIR / f"{slug}.json"

        if output_path.exists():
            print(f"[{i}/{total}] Skipping {slug} (already scraped)")
            continue

        print(f"[{i}/{total}] Scraping tweets: {name}")

        domain = (
            website
            .replace("https://", "")
            .replace("http://", "")
            .split("/")[0]
        )

        tweets = []
        for query in [name, domain]:
            results = scrape_tweets(query)
            tweets.extend(results)
            time.sleep(SLEEP_BETWEEN_QUERIES)

        data = {
            "startup": name,
            "slug": slug,
            "tweets": tweets
        }

        with open(output_path, "w") as f:
            json.dump(data, f)

        print(f"  Saved {len(tweets)} tweets to {output_path.name}")
        time.sleep(SLEEP_BETWEEN_STARTUPS)


if __name__ == "__main__":
    run()
