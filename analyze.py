from collections import Counter
import csv, sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else max(Path("logs").glob("*_keylog.csv"))
presses = 0
keys = Counter()

with open(path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["event"] == "press":
            presses += 1
            label = row["keysym"] or row["key"] or "<unknown>"
            keys[label] += 1

print(f"Analyzed: {path.name}")
print(f"Total key presses: {presses}")
print("Top 10 keys:")
for k, v in keys.most_common(10):
    print(f"{k:>12}  {v}")
