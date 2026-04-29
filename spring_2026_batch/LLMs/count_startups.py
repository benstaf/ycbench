import csv
import glob
import os
import re
from collections import Counter


def parse_startups(raw_text):
    startups = []
    for line in raw_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # Remove markdown bold markers (**)
        line = line.replace('**', '')
        # Remove leading numbering like "1." or "1. "
        line = re.sub(r'^\d+\.\s*', '', line)
        # Remove leading "- " (e.g. "- Matforge")
        line = re.sub(r'^-\s+', '', line)
        # Convert markdown links [text](url) → text (also handles nested: ([text](url)))
        line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
        # Remove leftover parenthesised chunks that are now empty or bare URLs
        line = re.sub(r'\(\s*https?://[^\)]*\)', '', line)
        line = re.sub(r'\(\s*\)', '', line)
        line = line.strip()
        # Normalise case: title-case for consistent grouping (e.g. matforge == Matforge)
        line = line.title()
        if line:
            startups.append(line)
    return startups


input_files = sorted(glob.glob('ycbench_p26_*.txt'))

if not input_files:
    print("No files found matching 'ycbench_p26_*.txt'")
    exit(1)

print(f"Found {len(input_files)} file(s)\n")

for input_path in input_files:
    stem = os.path.splitext(input_path)[0]
    output_path = stem + '_counts.csv'

    with open(input_path, 'r') as f:
        raw_text = f.read()

    startups = parse_startups(raw_text)
    counts = Counter(startups)
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Startup', 'Occurrences','Average (in percent)'])
        for rank, (name, count) in enumerate(ranked, 1):
            writer.writerow([rank, name, count,count*20])

    print(f"{input_path} → {output_path} ({len(ranked)} startups)")
