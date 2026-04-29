import json
import csv
import sys
from urllib.parse import urlparse

def extract_domain(url):
    if not url:
        return ""
    try:
        parsed = urlparse(url if url.startswith("http") else "https://" + url)
        domain = parsed.netloc.lstrip("www.")
        return domain
    except Exception:
        return url

def json_to_csv(input_file, output_file):
    with open(input_file) as f:
        companies = json.load(f)

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "domain", "website", "batch", "one_liner", "tags"])
        for c in companies:
            writer.writerow([
                c.get("name", ""),
                extract_domain(c.get("website", "")),
                c.get("website", ""),
                c.get("batch", ""),
                c.get("one_liner", ""),
                ", ".join(c.get("tags", [])),
            ])

    print(f"Wrote {len(companies)} rows to {output_file}")

if __name__ == "__main__":
    input_file  = sys.argv[1] if len(sys.argv) > 1 else "companies.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "companies.csv"
    json_to_csv(input_file, output_file)
