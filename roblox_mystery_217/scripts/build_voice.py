#!/usr/bin/env python3
"""Assembles the English voiceover from Higgsfield TTS takes (assets/audio/vo/<block>.mp3).
Each block is trimmed, processed (mom outside = distant/reverb, whisper = close/breathy),
placed on its story anchor -> voiceover.wav (48 kHz) + timings.json + voiceover_en.srt.
Fallback (free, offline): if a take is missing, Kokoro ONNX synthesizes it locally."""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))
from script import BLOCKS

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUD = os.path.join(ROOT, "assets", "audio")
VO = os.path.join(AUD, "vo")
OUT = os.path.join(ROOT, "output")
SR = 48000
TOTAL = 60.0


def load(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def ffx(a, chain):
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", chain, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                       input=a.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def kokoro(text, voice):
    from kokoro_onnx import Kokoro
    k = Kokoro("/opt/kokoro/kokoro-v1.0.onnx", "/opt/kokoro/voices-v1.0.bin")
    v = {"N": "am_eric", "M": "af_heart", "W": "af_heart"}[voice]
    s, sr = k.create(text, voice=v, speed=1.1 if voice == "N" else 0.92, lang="en-us")
    return ffx(np.asarray(s, np.float32), f"aresample={SR}") if sr != SR else s


def trim(a, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    s, e = max(idx[0] - int(0.02 * SR), 0), min(idx[-1] + int(0.06 * SR), len(a))
    return a[s:e]


def tighten(a, max_gap=0.22, thr_db=-40):
    """shorten long breaths/pauses inside a take (keeps fast TikTok pacing)"""
    hop = int(0.01 * SR)
    n = len(a) // hop
    e = 20 * np.log10(np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    keep = np.ones(n, bool)
    i = 0
    while i < n:
        if e[i] < thr_db:
            j = i
            while j < n and e[j] < thr_db:
                j += 1
            run = j - i
            lim = int(max_gap * SR / hop)
            if run > lim:
                cut0 = i + lim // 2
                keep[cut0: cut0 + run - lim] = False
            i = j
        else:
            i += 1
    out = a[: n * hop].reshape(n, hop)[keep].ravel()
    return np.concatenate([out, a[n * hop:]])


TEMPO = {"N": 1.12, "M": 1.0, "W": 1.0}
GAP = {"N": 0.18, "M": 0.45, "W": 0.35}


def sentences(text):
    text = text.replace("A.M.", "AM.")
    parts = re.findall(r"[^.!?]+(?:\.\.\.|[.!?])?", text)
    return [p.strip() for p in parts if p.strip()]


def pauses(a, min_len=0.16, thr_db=-38):
    hop = int(0.01 * SR)
    n = len(a) // hop
    e = 20 * np.log10(np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    quiet = e < thr_db
    out, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) * hop / SR >= min_len:
                out.append(((i + j) / 2) * hop / SR)
            i = j
        else:
            i += 1
    return out


def split_times(a, sents):
    """sentence boundaries: proportional by characters, snapped to the nearest real pause"""
    dur = len(a) / SR
    w = np.array([len(s) for s in sents], float)
    est = np.cumsum(w)[:-1] / w.sum() * dur
    ps = pauses(a)
    b = []
    for x in est:
        cand = [p for p in ps if abs(p - x) < 0.6 and (not b or p > b[-1] + 0.2)]
        b.append(min(cand, key=lambda p: abs(p - x)) if cand else x)
    edges = [0.0] + b + [dur]
    return [(edges[i], edges[i + 1]) for i in range(len(sents))]


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    os.makedirs(OUT, exist_ok=True)
    mix = np.zeros(int(TOTAL * SR), np.float32)
    cur, blocks_out, subs = 0.0, [], []
    for bid, voice, text, anchor, pause in BLOCKS:
        path = os.path.join(VO, f"{bid}.mp3")
        src = "higgsfield" if os.path.exists(path) else "kokoro-fallback"
        a = load(path) if os.path.exists(path) else kokoro(text, voice)
        a = trim(a)
        a = tighten(a, GAP[voice])
        if TEMPO[voice] != 1.0:
            a = ffx(a, f"atempo={TEMPO[voice]}")
        if voice == "M":
            a = ffx(a, "highpass=f=220,lowpass=f=3000,aecho=0.8:0.6:70|150:0.35|0.2,volume=0.8")
        elif voice == "W":
            a = ffx(a, "highpass=f=300,treble=g=4,volume=0.7")
        start = cur if anchor is None else max(anchor, cur)
        if anchor is not None and anchor < cur - 0.05:
            print(f"!! block {bid} pushed from {anchor:.2f} to {cur:.2f}")
        s = int(start * SR)
        n = min(len(a), len(mix) - s)
        mix[s:s + n] += a[:n]
        end = start + len(a) / SR
        sents = sentences(text)
        for (s0, s1), stext in zip(split_times(a, sents), sents):
            subs.append((start + s0, start + s1, stext.replace("Two seventeen.", "2:17").replace("AM.", "AM.")))
        blocks_out.append({"id": bid, "voice": voice, "text": text, "s": round(start, 3), "e": round(end, 3), "src": src})
        print(f"{bid} {voice} {start:6.2f}-{end:6.2f} ({end - start:4.2f}s) [{src}] {text[:60]}")
        cur = end + pause
    if cur > TOTAL - 1.5:
        print(f"!! voice runs until {cur:.2f}s")
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
    sf.write(os.path.join(AUD, "voiceover.wav"), mix, SR, subtype="PCM_24")
    json.dump({"blocks": blocks_out, "subs": subs}, open(os.path.join(AUD, "timings.json"), "w"), indent=1)
    # SRT: merge "2:17 AM" etc fine; keep max ~42 chars per line, 2 lines
    with open(os.path.join(OUT, "voiceover_en.srt"), "w") as f:
        for i, (a0, a1, t) in enumerate(subs, 1):
            words, lines, line = t.split(), [], ""
            for w in words:
                if len(line) + len(w) + 1 > 38 and line:
                    lines.append(line); line = w
                else:
                    line = (line + " " + w).strip()
            lines.append(line)
            f.write(f"{i}\n{srt_time(a0)} --> {srt_time(a1)}\n" + "\n".join(lines[:2]) + "\n\n")
    print("speech ends at", round(blocks_out[-1]["e"], 2), "s")


if __name__ == "__main__":
    main()
