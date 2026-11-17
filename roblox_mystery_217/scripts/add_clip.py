#!/usr/bin/env python3
"""usage: add_clip.py IDX URL [IDX URL ...] -> adds to assets/clips/clips.json"""
import json, os, sys
p = os.path.join(os.path.dirname(__file__), "..", "assets", "clips", "clips.json")
j = json.load(open(p))
a = sys.argv[1:]
for i in range(0, len(a), 2):
    j[str(int(a[i]))] = a[i + 1]
json.dump(j, open(p, "w"), indent=0, sort_keys=True)
