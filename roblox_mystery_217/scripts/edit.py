#!/usr/bin/env python3
"""Local editor: turns the Higgsfield stills into a 60 s 1080x1920 30 fps video.
Moves every still (zoom / pan / shake / flashes), draws word-by-word captions
(reference "In this town..." format: one word, centered, white bold, black outline),
pipes frames into FFmpeg and muxes the audio mix.  No paid services."""
import json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(__file__))
from script import RED, YELLOW

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HF = os.path.join(ROOT, "assets", "hf")
OUT = os.path.join(ROOT, "output")
W, H, FPS, DUR = 1080, 1920, 30, 60.0
NF = int(DUR * FPS)
FONT = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "Poppins-800.ttf"), 92)
FONT_BIG = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "Poppins-800.ttf"), 150)

# ---------------------------------------------------------------- shot list
# (start, image index, z0, z1, (fx0, fy0), (fx1, fy1), grade)
# z = zoom factor relative to "cover" fit, f = normalized focus point in the source
SUBS = json.load(open(os.path.join(ROOT, "assets", "audio", "timings.json")))["subs"]
S = lambda i: SUBS[i][0]          # start time of narration sentence i (shots follow the voice)

SHOTS = [
    (0.00, 1, 1.00, 1.30, (.50, .50), (.50, .47), "night"),     # hook: town push-in
    (1.40, 2, 1.15, 1.45, (.55, .55), (.60, .52), "night"),     # the rule sign
    (2.85, 9, 1.05, 1.35, (.53, .62), (.53, .64), "red"),       # "exactly 2:17 AM" teaser
    (S(1), 1, 1.45, 1.25, (.25, .45), (.30, .45), "night"),     # nobody knows who made the rule
    (S(2), 2, 1.60, 1.30, (.60, .52), (.60, .52), "night"),     # nobody explains why
    (S(3), 3, 1.05, 1.35, (.55, .55), (.58, .55), "night"),     # every curtain closes
    (8.90, 1, 1.10, 1.18, (.50, .50), (.50, .50), "night"),     # lights on ...
    (9.85, 4, 1.18, 1.26, (.50, .50), (.50, .50), "dark"),      # ... lights OUT
    (S(5), 5, 1.05, 1.25, (.40, .58), (.48, .58), "day"),       # my name is Alex
    (12.20, 5, 1.55, 1.75, (.38, .55), (.38, .52), "day"),      # story to scare kids
    (S(7), 6, 1.00, 1.15, (.55, .55), (.58, .55), "night"),     # until last night
    (S(8), 7, 1.00, 1.40, (.48, .45), (.48, .40), "night"),     # almost asleep... creeping in
    (17.25, 8, 2.00, 2.10, (.17, .58), (.17, .58), "night"),    # KNOCKS (outside silhouette)
    (S(10), 10, 1.05, 1.25, (.45, .45), (.45, .40), "night"),   # three knocks, on my window
    (S(12), 9, 1.05, 1.20, (.53, .60), (.53, .62), "red"),     # checks the clock
    (S(13), 9, 1.40, 1.85, (.53, .64), (.53, .64), "red"),      # 2:17 AM
    (S(15), 7, 1.25, 1.50, (.48, .40), (.48, .40), "night"),    # mom's voice from outside
    (S(17), 11, 1.00, 1.30, (.50, .50), (.50, .50), "night"),   # "Alex... please let me in"
    (S(20), 13, 1.05, 1.25, (.45, .45), (.40, .40), "night"),   # I looked
    (S(22), 11, 1.60, 2.00, (.50, .45), (.50, .45), "night"),   # smiling
    (S(23), 12, 1.00, 1.15, (.55, .50), (.55, .45), "night"),   # same sweater, same smile
    (S(25), 12, 1.45, 1.85, (.62, .40), (.62, .38), "night"),   # she didn't blink
    (S(27), 14, 1.15, 1.05, (.50, .55), (.50, .55), "night"),   # HAND ON SHOULDER
    (S(28), 14, 1.70, 1.90, (.30, .50), (.30, .48), "night"),   # real mom behind me
    (S(29), 15, 1.05, 1.30, (.62, .35), (.62, .32), "night"),   # don't look at her
    (S(30), 16, 1.05, 1.25, (.35, .40), (.35, .38), "night"),   # I turned back
    (S(31), 14, 1.90, 2.30, (.73, .50), (.73, .48), "night"),   # she was still there
    (S(32), 17, 1.00, 1.20, (.50, .55), (.50, .55), "fog"),     # next morning
    (S(33), 17, 1.45, 1.70, (.30, .55), (.40, .55), "fog"),     # every single house
    (S(34), 18, 1.05, 1.30, (.55, .45), (.60, .42), "fog"),     # staring into the windows
    (S(35), 19, 1.05, 1.40, (.50, .50), (.50, .47), "fog"),     # every one of them
    (S(36), 19, 1.60, 1.80, (.50, .47), (.50, .47), "fog"),     # terrified
    (SUBS[36][1], 19, 1.80, 1.82, (.50, .47), (.50, .47), "silence"),  # silence beat
    (S(37), 20, 1.00, 1.25, (.50, .50), (.50, .48), "night"),   # the rule was never...
    (S(38), 21, 1.00, 1.45, (.52, .47), (.52, .46), "night"),   # protecting them...
    (S(39), 21, 2.30, 2.60, (.52, .455), (.52, .455), "night"),   # ...from us (snap zoom)
]
PRECROP = {9: (0.0, 0.0, 0.78, 0.775)}
END_CARD = 58.55
BURN_CAPTIONS = False   # captions are added inside TikTok by the creator   # "PART 2" + knocks

# events: (time, kind, strength)
EVENTS = [(0.0, "flash", 0.7), (2.85, "flash_red", 0.6), (9.85, "flicker", 1.0),
          (17.25, "shake", 1.0), (17.7, "shake", 1.0), (18.15, "shake", 1.0),
          (S(13), "flash_red", 0.9), (S(13), "shake", 0.6), (S(27) + 0.55, "shake", 1.2), (S(27) + 0.55, "flash", 0.5),
          (S(31), "flash", 0.35), (S(37), "flash", 0.6), (S(39) + 0.3, "flash", 0.9), (S(39) + 0.3, "shake", 1.2),
          (58.65, "shake", 0.9), (59.1, "shake", 0.9), (59.55, "shake", 0.9)]


def ease(x):
    return x * x * (3 - 2 * x)


_cache = {}


def src(idx):
    if idx not in _cache:
        f = [p for p in os.listdir(HF) if p.startswith(f"{idx:02d}_")][0]
        im = Image.open(os.path.join(HF, f)).convert("RGB")
        if idx in PRECROP:  # remove unwanted borders (e.g. editor UI) instead of paying for a re-roll
            l, tp, r, b = PRECROP[idx]
            im = im.crop((int(l * im.width), int(tp * im.height), int(r * im.width), int(b * im.height)))
        _cache[idx] = im
    return _cache[idx]


def grade(im, g, t):
    if g in ("night", "dark"):
        im = ImageEnhance.Contrast(im).enhance(1.08)
        a = np.asarray(im, np.float32)
        a[..., 2] *= 1.04; a[..., 0] *= 0.97
        if g == "dark":
            a *= 0.85
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    elif g == "red":
        im = ImageEnhance.Contrast(im).enhance(1.15)
    elif g == "fog":
        im = ImageEnhance.Color(im).enhance(0.75)
    elif g == "silence":
        im = ImageEnhance.Color(im).enhance(0.15)
        im = ImageEnhance.Brightness(im).enhance(0.55)
    return im


def shot_at(t):
    cur = SHOTS[0]
    for i, s in enumerate(SHOTS):
        if s[0] <= t:
            cur = s; nxt = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
    return cur, nxt


def shake_offset(t):
    dx = dy = 0.0
    for et, kind, st in EVENTS:
        if kind == "shake" and 0 <= t - et < 0.35:
            d = (t - et) / 0.35
            amp = 26 * st * (1 - d) ** 2
            dx += amp * math.sin(t * 97.0); dy += amp * math.cos(t * 83.0)
    # constant subtle handheld drift (Roblox camera feel)
    dx += 3.0 * math.sin(t * 1.3); dy += 2.5 * math.sin(t * 1.7 + 1)
    return dx, dy


def render_bg(t):
    (st, idx, z0, z1, f0, f1, g), nxt = shot_at(t)
    p = ease(min(max((t - st) / max(nxt - st, 0.01), 0), 1))
    z = max(z0 + (z1 - z0) * p, 1.04)
    fx = f0[0] + (f1[0] - f0[0]) * p
    fy = f0[1] + (f1[1] - f0[1]) * p
    im = src(idx)
    sw, sh = im.size
    cover = max(W / sw, H / sh)
    scale = cover * z
    cw, ch = W / scale, H / scale
    dx, dy = shake_offset(t)
    cx = min(max(fx * sw - dx / scale, cw / 2), sw - cw / 2)
    cy = min(max(fy * sh - dy / scale, ch / 2), sh - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    fr = im.resize((W, H), Image.BICUBIC, box=box, reducing_gap=None)
    return grade(fr, g, t)


def overlays(fr, t):
    a = np.asarray(fr, np.float32)
    for et, kind, st in EVENTS:
        d = t - et
        if kind == "flash" and 0 <= d < 0.25:
            a += (255 - a) * st * (1 - d / 0.25) ** 2
        if kind == "flash_red" and 0 <= d < 0.35:
            k = st * (1 - d / 0.35) ** 2
            a[..., 0] += (255 - a[..., 0]) * k * 0.8; a[..., 1] *= 1 - 0.5 * k; a[..., 2] *= 1 - 0.5 * k
        if kind == "flicker" and 0 <= d < 0.4:
            if int(d * 30) % 2 == 0:
                a *= 0.35
    # vignette
    yy, xx = np.ogrid[:H, :W]
    if not hasattr(overlays, "vig"):
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        overlays.vig = np.clip(1 - 0.38 * np.clip(r - 0.55, 0, 1) ** 1.5, 0, 1)[..., None].astype(np.float32)
    a *= overlays.vig
    # light film grain (deterministic per frame)
    rng = np.random.default_rng(int(t * FPS))
    a += rng.normal(0, 4.0, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


WORDS = []  # word-level captions disabled (captions are added in TikTok)


def caption(fr, t):
    cur = None
    for w in WORDS:
        if w["s"] - 0.02 <= t < w["e"] + 0.12:
            cur = w
    if cur is None or t >= END_CARD:
        return fr
    raw = cur["w"]
    clean = raw.strip(",.…!?\"")
    text = clean.lower() if not any(ch.isdigit() for ch in clean) else clean
    if clean.upper() == "AM":
        text = "AM"
    col = (255, 255, 255)
    if raw in RED or clean in RED:
        col = (255, 48, 48)
    elif raw in YELLOW or clean in YELLOW:
        col = (255, 214, 0)
    if cur["voice"] in ("M", "W"):          # mom's lines: italic-ish feel via color tint
        col = (255, 120, 120) if cur["voice"] == "M" else (190, 210, 255)
    pop = min((t - cur["s"]) / 0.09, 1.0)
    size = int(92 * (1.18 - 0.18 * ease(max(pop, 0))))
    font = FONT.font_variant(size=size)
    d = ImageDraw.Draw(fr)
    y = int(H * 0.645)                      # same height as the reference, inside TikTok safe zone
    d.text((W // 2 + 4, y + 6), text, font=font, anchor="mm", fill=(0, 0, 0), stroke_width=9, stroke_fill=(0, 0, 0))
    d.text((W // 2, y), text, font=font, anchor="mm", fill=col, stroke_width=7, stroke_fill=(0, 0, 0))
    return fr


def end_card(fr, t):
    if t < END_CARD:
        return fr
    k = min((t - END_CARD) / 0.25, 1)
    d = ImageDraw.Draw(fr)
    y = int(H * 0.70)
    d.text((W // 2, y), "PART 2", font=FONT_BIG.font_variant(size=int(150 * (1.3 - 0.3 * k))), anchor="mm",
           fill=(255, 40, 40), stroke_width=10, stroke_fill=(0, 0, 0))
    d.text((W // 2, y + 140), "follow so you don't miss it", font=FONT.font_variant(size=54), anchor="mm",
           fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    return fr


def frame(i):
    t = i / FPS
    fr = render_bg(t)
    fr = overlays(fr, t)
    if BURN_CAPTIONS:
        fr = caption(fr, t)
    fr = end_card(fr, t)
    return fr.tobytes()


def main():
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]  # optional: list of seconds -> preview PNGs
    if only:
        for s in only:
            Image.frombytes("RGB", (W, H), frame(int(float(s) * FPS))).save(f"/tmp/claude-0/prev_{s}.jpg", quality=85)
        return
    silent = os.path.join(OUT, "_video_noaudio.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for n, b in enumerate(pool.imap(frame, range(NF), chunksize=8)):
            ff.stdin.write(b)
            if n % 300 == 0:
                print("frame", n, flush=True)
    ff.stdin.close(); ff.wait()
    print("video done")


if __name__ == "__main__":
    main()
