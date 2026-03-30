import json
import logging
import os
import time

import requests
import pandas as pd
from pathlib import Path

# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
FEATURE_DIR = DATA_DIR / "features"

OUTPUT_DIR = RAW_DIR / "reddit"
FEATURE_FILE = FEATURE_DIR / "reddit_metrics.json"
LOG_FILE = FEATURE_DIR / "reddit_scrape.log"

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
TARGET_BATCH = "W26"

# --------------------------------------------------
# Reddit OAuth credentials
# Register a "script" app at https://www.reddit.com/prefs/apps
# Then set these env vars (or replace with your values directly):
#   REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
#   REDDIT_USERNAME, REDDIT_PASSWORD
# --------------------------------------------------
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "YOUR_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME", "YOUR_USERNAME")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD", "YOUR_PASSWORD")
REDDIT_USER_AGENT = "ycbench/1.0 (by /u/" + REDDIT_USERNAME + ")"

REQUEST_TIMEOUT = 15

# --------------------------------------------------
# Reddit OAuth token management
# --------------------------------------------------
_reddit_token: str | None = None
_reddit_token_expiry: float = 0.0


def get_reddit_token() -> str:
    global _reddit_token, _reddit_token_expiry
    if _reddit_token and time.time() < _reddit_token_expiry - 60:
        return _reddit_token

    r = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET),
        data={
            "grant_type": "password",
            "username": REDDIT_USERNAME,
            "password": REDDIT_PASSWORD,
        },
        headers={"User-Agent": REDDIT_USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    _reddit_token = data["access_token"]
    _reddit_token_expiry = time.time() + data.get("expires_in", 3600)
    log.info("Obtained Reddit OAuth token.")
    return _reddit_token


def reddit_headers() -> dict:
    return {
        "Authorization": f"bearer {get_reddit_token()}",
        "User-Agent": REDDIT_USER_AGENT,
    }


# --------------------------------------------------
# Query Builder
# --------------------------------------------------

def build_queries(name: str, batch: str) -> list[str]:
    return [
        f'"{name}" YC',
        f'"{name}" "Y Combinator"',
        f'"{name}" {batch}',
    ]


# --------------------------------------------------
# Reddit Post Search  (OAuth – oauth.reddit.com)
# --------------------------------------------------

def search_reddit_posts(query: str, domain: str | None = None) -> list[dict]:
    url = (
        "https://oauth.reddit.com/search.json"
        f"?q={requests.utils.quote(query)}"
        "&limit=100"
        "&sort=relevance"
        "&type=link"
    )
    try:
        r = requests.get(
            url,
            headers=reddit_headers(),
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        posts = [p["data"] for p in r.json()["data"]["children"]]
        if domain:
            posts = [p for p in posts if domain in p.get("url", "")]
        return posts
    except Exception as e:
        log.error(f"Post search failed for '{query}': {e}")
        return []


# --------------------------------------------------
# Pullpush Comment Search  (community Pushshift replacement)
# Docs: https://pullpush.io
# --------------------------------------------------

def search_reddit_comments(query: str) -> list[dict]:
    url = (
        "https://api.pullpush.io/reddit/search/comment/"
        f"?q={requests.utils.quote(query)}"
        "&size=100"
    )
    try:
        r = requests.get(
            url,
            headers={"User-Agent": REDDIT_USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        return r.json().get("data", [])
    except Exception as e:
        log.warning(f"Comment search failed for '{query}': {e}")
        return []


# --------------------------------------------------
# Aggregate Reddit Score
# --------------------------------------------------

def get_reddit_score(
    name: str, batch: str, domain: str | None = None
) -> tuple[float, list, list, int, int, int]:
    queries = build_queries(name, batch)

    all_posts: dict[str, dict] = {}
    all_comments: dict[str, dict] = {}

    for query in queries:
        for p in search_reddit_posts(query, domain):
            all_posts[p["id"]] = p
        for c in search_reddit_comments(query):
            all_comments[c["id"]] = c
        time.sleep(1)  # stay within Reddit's 60 req/min OAuth rate limit

    posts = list(all_posts.values())
    comments = list(all_comments.values())

    high_score_posts = sum(1 for p in posts if p.get("score", 0) > 100)
    total_upvotes = sum(p.get("score", 0) for p in posts)
    total_post_comments = sum(p.get("num_comments", 0) for p in posts)

    score = len(posts) + (len(comments) / 5) + (5 * high_score_posts)

    return score, posts, comments, total_upvotes, total_post_comments, high_score_posts


# --------------------------------------------------
# Main Runner
# --------------------------------------------------

def run():
    log.info("Fetching YC batch dataset...")
    r = requests.get(BATCH_JSON_URL, timeout=REQUEST_TIMEOUT)
    df = pd.DataFrame(r.json())

    features: dict[str, dict] = {}
    no_results: list[str] = []

    for _, row in df.iterrows():
        name = row["name"]
        slug = row["slug"]
        domain = row.get("website", "")

        (
            score,
            posts,
            comments,
            upvotes,
            post_comment_count,
            high_score_posts,
        ) = get_reddit_score(name, TARGET_BATCH, domain)

        time.sleep(2)  # polite crawl delay between companies

        if not posts and not comments:
            log.warning(
                f"NO RESULTS   {name} "
                f"(slug={slug}, domain={domain or 'n/a'})"
            )
            no_results.append(name)
        else:
            log.info(
                f"OK           {name} — "
                f"{len(posts)} posts, {len(comments)} comments "
                f"(score={score:.1f})"
            )
            with open(OUTPUT_DIR / f"{slug}.json", "w") as f:
                json.dump({"posts": posts, "comments": comments}, f)

        features[slug] = {
            "reddit_score": score,
            "reddit_posts": len(posts),
            "reddit_comments_found": len(comments),
            "reddit_high_score_posts": high_score_posts,
            "reddit_upvotes": upvotes,
            "reddit_post_comment_count": post_comment_count,
        }

    with open(FEATURE_FILE, "w") as f:
        json.dump(features, f, indent=2)

    log.info("=" * 60)
    log.info(
        f"Done. {len(df) - len(no_results)}/{len(df)} startups had Reddit results."
    )
    if no_results:
        log.warning(f"{len(no_results)} with no results: {', '.join(no_results)}")
    log.info(f"Full log saved to: {LOG_FILE}")


# --------------------------------------------------
if __name__ == "__main__":
    run()
