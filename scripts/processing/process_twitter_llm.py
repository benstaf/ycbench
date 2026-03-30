import json
import os
import requests
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
FEATURE_DIR = DATA_DIR / "features"

INPUT_DIR = RAW_DIR / "tweets"
OUTPUT_FILE = FEATURE_DIR / "twitter_metrics.json"

FEATURE_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Config
# --------------------------------------------------

DEEPINFRA_API_KEY = "YOUR_KEY"
MODEL = "deepseek-ai/DeepSeek-V3.2"

API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"

# --------------------------------------------------

def extract_metrics(tweets, company):

    text = "\n".join(
        t.get("full_text", t.get("text", ""))
        for t in tweets
    )[:8000]

    prompt = f"""
Extract ARR and funding numbers.

Startup: {company}

Return JSON:
{{"arr": number, "funding": number}}

Tweets:
{text}
"""

    headers = {
        "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    try:

        r = requests.post(API_URL, headers=headers, json=payload)

        raw = r.json()["choices"][0]["message"]["content"]

        parsed = json.loads(raw)

        return {
            "arr": parsed.get("arr", 0),
            "funding": parsed.get("funding", 0)
        }

    except Exception:
        return {"arr": 0, "funding": 0}


# --------------------------------------------------

def run():

    results = {}

    for file in os.listdir(INPUT_DIR):

        if not file.endswith(".json"):
            continue

        path = INPUT_DIR / file

        with open(path) as f:
            data = json.load(f)

        slug = data["slug"]
        tweets = data["tweets"]

        print("Processing", slug)

        metrics = extract_metrics(tweets, slug)

        results[slug] = metrics

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    run()
