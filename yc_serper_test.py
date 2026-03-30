import requests


d = "trycardinal.ai"

r = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
    json={
        "q": f'"{d}"',
        "num": 10,
        "tbs": "cdr:1,cd_min:01/01/2026"  # results from Jan 1 2026 onwards
    },
    timeout=10
)

data = r.json()
print("Full response:")
import json
print(json.dumps(data, indent=2))
