import json
import logging
import time

import requests
import pandas as pd
from pathlib import Path

# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
FEATURE_DIR = DATA_DIR / "features"

OUTPUT_DIR = RAW_DIR / "hn"
FEATURE_FILE = FEATURE_DIR / "hn_metrics.json"
LOG_FILE = FEATURE_DIR / "hn_scrape.log"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FEATURE_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# --------------------------------------------------
BATCH_JSON_URL = "https://yc-oss.github.io/api/batches/winter-2026.json"


def get_hn_score(name, domain=None):
    query = name.replace(" ", "+")
    url = (
        f"https://hn.algolia.com/api/v1/search"
        f"?query={query}"
        f"&tags=(story,comment)"  # parentheses = OR (comma alone means AND)
        f"&hitsPerPage=100"
    )

    try:
        hits = requests.get(url).json()["hits"]

        # Filter to relevant hits if a domain is available
        if domain:
            hits = [h for h in hits if domain in h.get("url", "")]

        frontpage = sum(1 for h in hits if h.get("points", 0) > 50)
        score = 5 * frontpage + len(hits)

        return score, hits

    except Exception as e:
        log.error(f"Error fetching HN data for '{name}': {e}")
        return 0, []


def run():
    r = requests.get(BATCH_JSON_URL)
    df = pd.DataFrame(r.json())
    features = {}
    no_results = []

    for _, row in df.iterrows():
        name = row["name"]
        slug = row["slug"]
        domain = row.get("website", "")

        score, hits = get_hn_score(name, domain=domain)
        time.sleep(1)

        if not hits:
            log.warning(f"NO RESULTS   {name} (slug={slug}, domain={domain or 'n/a'})")
            no_results.append(name)
        else:
            frontpage = sum(1 for h in hits if h.get("points", 0) > 50)
            log.info(f"OK           {name} — {len(hits)} hits, {frontpage} frontpage (score={score})")

        if hits:
            with open(OUTPUT_DIR / f"{slug}.json", "w") as f:
                json.dump({"stories": hits}, f)

        features[slug] = {"hn_score": score}

    with open(FEATURE_FILE, "w") as f:
        json.dump(features, f, indent=2)

    log.info("=" * 60)
    log.info(f"Done. {len(df) - len(no_results)}/{len(df)} startups had HN results.")
    if no_results:
        log.warning(f"{len(no_results)} with no results: {', '.join(no_results)}")
    log.info(f"Full log saved to: {LOG_FILE}")


if __name__ == "__main__":
    run()
