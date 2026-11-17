#!/usr/bin/env python3
"""Download animated Higgsfield clips listed in assets/clips/clips.json and extract frames (24 fps JPG)."""
import json, os, subprocess
D = os.path.join(os.path.dirname(__file__), "..", "assets", "clips")
for idx, url in sorted(json.load(open(os.path.join(D, "clips.json"))).items(), key=lambda x: int(x[0])):
    mp4 = os.path.join(D, f"{int(idx):02d}.mp4")
    if not os.path.exists(mp4):
        subprocess.run(["curl", "-sS", "-o", mp4, url], check=True)
    fd = os.path.join(D, f"{int(idx):02d}")
    if not os.path.isdir(fd):
        os.makedirs(fd)
        subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "fps=24", "-q:v", "2", os.path.join(fd, "%04d.jpg")], check=True)
        print("frames", idx, len(os.listdir(fd)))
