import json
import numpy as np
import pandas as pd
import requests
from pathlib import Path

# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
FEATURE_DIR = DATA_DIR / "features"
RESULT_DIR = DATA_DIR / "results"

RESULT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RESULT_DIR / "yc_predemo_scores.csv"

# --------------------------------------------------

BATCH_JSON_URL = "https://yc-oss.github.io/api/batches/winter-2026.json"

WEIGHTS = {
    "arr": 0.4,
    "funding": 0.25,
    "github": 0.25,
    "hn": 0.10
}


def robust_z(x):

    median = np.median(x)
    mad = np.median(np.abs(x - median))

    return (x - median) / (mad + 1e-8)


def load_json(path):

    with open(path) as f:
        return json.load(f)


# --------------------------------------------------

def run():

    r = requests.get(BATCH_JSON_URL)
    batch = pd.DataFrame(r.json())[["name", "slug"]]

    twitter = load_json(FEATURE_DIR / "twitter_metrics.json")
    github = load_json(FEATURE_DIR / "github_metrics.json")
    hn = load_json(FEATURE_DIR / "hn_metrics.json")

    rows = []

    for _, row in batch.iterrows():

        slug = row["slug"]

        arr = twitter.get(slug, {}).get("arr", 0)
        funding = twitter.get(slug, {}).get("funding", 0)
        forks = github.get(slug, {}).get("fork_growth", 0)
        hn_score = hn.get(slug, {}).get("hn_score", 0)

        rows.append({
            "name": row["name"],
            "arr": arr,
            "funding": funding,
            "forks": forks,
            "hn": hn_score
        })

    df = pd.DataFrame(rows)

    df["z_arr"] = robust_z(df["arr"])
    df["z_funding"] = robust_z(df["funding"])
    df["z_forks"] = robust_z(df["forks"])
    df["z_hn"] = robust_z(df["hn"])

    df["score"] = (
        WEIGHTS["arr"] * df["z_arr"]
        + WEIGHTS["funding"] * df["z_funding"]
        + WEIGHTS["github"] * df["z_forks"]
        + WEIGHTS["hn"] * df["z_hn"]
    )

    df = df.sort_values("score", ascending=False)

    return df


if __name__ == "__main__":

    df = run()

    df.to_csv(OUTPUT_FILE, index=False)

    print(df.head(20))
