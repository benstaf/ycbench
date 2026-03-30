import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
FEATURE_DIR = DATA_DIR / "features"

OUTPUT_DIR = RAW_DIR / "github"
FEATURE_FILE = FEATURE_DIR / "github_metrics.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FEATURE_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------

BATCH_JSON_URL = "https://yc-oss.github.io/api/batches/winter-2026.json"

START_DATE = "2026-01-01"
END_DATE = "2026-03-24"


# --------------------------------------------------

def find_repo(name):

    query = name.replace(" ", "+")

    url = f"https://api.github.com/search/repositories?q={query}&sort=forks&order=desc"

    try:

        r = requests.get(url)
        items = r.json().get("items", [])

        if items:
            return items[0]["full_name"]

    except:
        pass

    return None


def get_fork_delta(repo):

    if not repo:
        return 0

    owner, name = repo.split("/")

    url = f"https://api.github.com/repos/{owner}/{name}/forks?per_page=100"

    try:

        forks = requests.get(url).json()

        start = datetime.fromisoformat(START_DATE).timestamp()
        end = datetime.fromisoformat(END_DATE).timestamp()

        delta = 0

        for f in forks:

            ts = datetime.fromisoformat(
                f["created_at"].replace("Z","")
            ).timestamp()

            if start <= ts <= end:
                delta += 1

        return delta

    except:
        return 0


# --------------------------------------------------

def run():

    r = requests.get(BATCH_JSON_URL)
    df = pd.DataFrame(r.json())

    features = {}

    for _, row in df.iterrows():

        name = row["name"]
        slug = row["slug"]

        print("GitHub:", name)

        repo = find_repo(name)
        forks = get_fork_delta(repo)

        data = {
            "repo": repo,
            "fork_growth": forks
        }

        with open(OUTPUT_DIR / f"{slug}.json", "w") as f:
            json.dump(data, f)

        features[slug] = data

    with open(FEATURE_FILE, "w") as f:
        json.dump(features, f, indent=2)


if __name__ == "__main__":
    run()
