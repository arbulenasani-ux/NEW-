#!/usr/bin/env python3
"""Download Higgsfield results listed in assets/hf/jobs.json -> assets/hf/NN_name.png (later converted to JPG q95 to keep the repo small)"""
import json, os, sys, subprocess
D = os.path.join(os.path.dirname(__file__), "..", "assets", "hf")
jobs = json.load(open(os.path.join(D, "jobs.json")))
for idx, (name, url) in sorted(jobs.items(), key=lambda x: int(x[0])):
    out = os.path.join(D, f"{int(idx):02d}_{name}.png")
    if not os.path.exists(out) and url:
        subprocess.run(["curl", "-sS", "-o", out, url], check=True)
        print("got", out)
