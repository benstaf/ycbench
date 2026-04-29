import csv
import glob
from collections import defaultdict

input_files = sorted(glob.glob('ycbench_p26_*_counts.csv'))

if not input_files:
    print("No files found matching 'ycbench_p26_*_counts.csv'")
    exit(1)

print(f"Found {len(input_files)} CSV file(s)\n")

counts = defaultdict(int)
all_startups = set()

for path in input_files:
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['Startup']
            all_startups.add(name)
            counts[name] += int(row['Occurrences'])

n = len(input_files)
averaged = {name: counts[name] / n for name in all_startups}
scaled = {name: averaged[name] * 20 for name in all_startups}
ranked = sorted(scaled.items(), key=lambda x: x[1], reverse=True)

output_path = 'ycbench_p26_aggregate.csv'
with open(output_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Rank', 'Startup', 'Avg Occurrences', 'Score (x20)'])
    for rank, (name, score) in enumerate(ranked, 1):
        writer.writerow([rank, name, round(averaged[name], 4), round(score, 4)])

print(f"Aggregated {len(ranked)} startups across {n} files â†’ '{output_path}'")
for rank, (name, score) in enumerate(ranked, 1):
    print(f"{rank:2}. {name} â€” avg {averaged[name]:.4f} â†’ score {score:.4f}")
