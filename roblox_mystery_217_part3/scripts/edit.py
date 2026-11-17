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
W, H, FPS, DUR = 1080, 1920, 30, 61.0
NF = int(DUR * FPS)
FONT = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "Poppins-800.ttf"), 92)
FONT_BIG = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", "Poppins-800.ttf"), 150)

# ---------------------------------------------------------------- shot list
# (start, image index, z0, z1, (fx0, fy0), (fx1, fy1), grade)
# z = zoom factor relative to "cover" fit, f = normalized focus point in the source
SUBS = json.load(open(os.path.join(ROOT, "assets", "audio", "timings.json")))["subs"]
S = lambda i: SUBS[i][0]          # start time of narration sentence i (shots follow the voice)

SHOTS = [
    (0.00, 1, 1.00, 1.08, (.50, .45), (.50, .42), "night"),     # never trust your reflection
    (S(1), 1, 1.10, 1.20, (.50, .38), (.50, .36), "night"),     # the boy in the puddle smiled
    (S(2), 2, 1.00, 1.10, (.50, .40), (.50, .38), "night"),     # but I wasn't smiling
    (S(3), 3, 1.00, 1.08, (.40, .50), (.40, .48), "night"),     # don't look at him, Alex
    (S(4), 3, 1.15, 1.25, (.30, .40), (.30, .38), "night"),     # that thing wants your place
    (S(5), 7, 1.00, 1.08, (.50, .45), (.50, .42), "night"),     # mom told me the truth
    (S(6), 4, 1.00, 1.10, (.60, .45), (.62, .43), "night"),     # things inside look out the windows
    (S(7), 5, 1.00, 1.08, (.50, .45), (.48, .42), "night"),     # if you look back...
    (S(8), 5, 1.15, 1.25, (.42, .35), (.42, .33), "night"),     # they take your place
    (S(9), 10, 1.00, 1.10, (.50, .55), (.50, .52), "fog"),      # people outside so scared
    (S(10), 10, 1.15, 1.20, (.50, .50), (.50, .48), "fog"),     # they weren't the monsters
    (S(11), 6, 1.00, 1.10, (.80, .58), (.80, .56), "fog"),      # the real families
    (S(12), 6, 1.35, 1.50, (.88, .60), (.88, .58), "fog"),      # locked out of their homes
    (S(13), 7, 1.15, 1.25, (.40, .62), (.40, .60), "night"),    # three years (photo)
    (S(14), 8, 1.00, 1.12, (.50, .40), (.50, .36), "night"),    # one way back inside
    (S(15), 1, 1.15, 1.25, (.50, .36), (.50, .35), "night"),    # make your reflection look away first
    (S(16), 8, 1.70, 2.00, (.50, .32), (.50, .32), "night"),    # before the clock hits 2:18
    (S(17), 9, 1.00, 1.08, (.50, .45), (.50, .43), "night"),    # I stared at him
    (S(18), 9, 1.15, 1.20, (.40, .42), (.40, .41), "night"),    # he stared at me
    (S(19), 9, 1.25, 1.35, (.30, .42), (.30, .41), "night"),    # ten seconds
    (S(20), 9, 1.30, 1.40, (.62, .40), (.62, .40), "night"),    # twenty
    (S(21), 11, 1.00, 1.10, (.50, .40), (.50, .40), "night"),   # the church bell rang
    (S(22), 1, 1.30, 1.40, (.50, .35), (.50, .35), "night"),    # he blinked
    (S(23), 1, 1.00, 1.05, (.50, .45), (.50, .45), "dark"),     # the puddle went dark
    (S(24), 12, 1.00, 1.15, (.50, .50), (.50, .48), "dark"),    # every window went black
    (S(25), 13, 1.00, 1.08, (.40, .55), (.40, .53), "day"),     # opened my eyes in my room
    (S(26), 13, 1.25, 1.40, (.40, .62), (.40, .62), "day"),     # my real mom holding my hand
    (S(27), 14, 1.00, 1.10, (.55, .55), (.55, .52), "day"),     # people finally went home
    (S(28), 15, 1.00, 1.08, (.50, .50), (.50, .48), "night"),   # this town has a new rule
    (S(29), 16, 2.20, 2.40, (.25, .555), (.25, .555), "red"),    # at 2:17 AM (sharp 2K still)
    (S(30), 15, 1.35, 1.50, (.30, .38), (.30, .36), "night"),   # something looks at you
    (S(31), 15, 1.05, 1.15, (.50, .45), (.50, .42), "night"),   # don't look away
]
# only the usable start of some clips (later frames drift: figures fade into fog / face changes)
CLIP_MAXT = {3: 1.9, 10: 1.2, 14: 2.4}


def _plan_clip_offsets():
    """reused images continue their clip where the last use stopped; long shots play slower"""
    used = {}
    for i, sh in enumerate(SHOTS):
        st, idx = sh[0], sh[1]
        nxt = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
        d = os.path.join(CLIPS, f"{idx:02d}")
        if not os.path.isdir(d):
            continue
        clen = len([f for f in os.listdir(d) if f.endswith(".jpg")]) / 24.0
        clen = min(clen, CLIP_MAXT.get(idx, clen))
        dur = nxt - st
        off = used.get(idx, 0.0)
        if off > clen - 0.6:
            off = 0.0
        spd = min(1.0, max((clen - off) / dur, 0.35))
        CLIP_OFF[st] = (off, spd)
        used[idx] = off + dur * spd


PRECROP = {}
END_CARD = 58.3
BURN_CAPTIONS = False   # captions are added inside TikTok by the creator   # "THE END" + knocks

# events: (time, kind, strength)
EVENTS = [(0.0, "flash", 0.6), (S(8), "flash", 0.4), (S(13) + 0.3, "flash", 0.2),
          (SUBS[21][1] + 0.95, "flash", 0.8), (SUBS[21][1] + 0.95, "shake", 1.2),
          (S(22) + 0.35, "flash", 0.6), (S(22) + 0.35, "shake", 0.8),
          (S(31) + 0.2, "flash", 0.8), (S(31) + 0.2, "shake", 1.0), (58.4, "shake", 0.6)]


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


CLIPS = os.path.join(ROOT, "assets", "clips")   # animated Higgsfield clips, frames extracted to NN/0001.jpg
CLIP_OFF = {}    # per shot start time -> offset (s) inside the clip; filled below SHOTS
_fcache = {}


def clip_frame(idx, ct):
    """frame of the animated clip for image idx at clip time ct (None if no clip)"""
    d = os.path.join(CLIPS, f"{idx:02d}")
    if not os.path.isdir(d):
        return None
    if idx not in _fcache:
        _fcache[idx] = sorted(f for f in os.listdir(d) if f.endswith(".jpg"))
    files = _fcache[idx]
    fps = 24.0
    i = int(ct * fps)
    i = min(max(i, 0), len(files) - 1)
    im = Image.open(os.path.join(d, files[i])).convert("RGB")
    if idx in PRECROP:
        l, tp, r, b = PRECROP[idx]
        im = im.crop((int(l * im.width), int(tp * im.height), int(r * im.width), int(b * im.height)))
    return im


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
    off, spd = CLIP_OFF.get(st, (0.0, 1.0))
    cf = clip_frame(idx, off + (t - st) * spd)
    if cf is not None:   # QUALITY: clips are full-HD and move by themselves -> almost no digital zoom
        z = min(max(1.0 + (z - 1.0) * 0.6, 1.03), 1.45)
    im = cf or src(idx)
    sw, sh = im.size
    cover = max(W / sw, H / sh)
    scale = cover * z
    cw, ch = W / scale, H / scale
    dx, dy = shake_offset(t)
    cx = min(max(fx * sw - dx / scale, cw / 2), sw - cw / 2)
    cy = min(max(fy * sh - dy / scale, ch / 2), sh - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    fr = im.resize((W, H), Image.LANCZOS, box=box, reducing_gap=None)
    fr = fr.filter(ImageFilter.UnsharpMask(radius=1.2, percent=45, threshold=2))
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
    # QUALITY: no film grain (it made the encode soft and big)
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
    y = int(H * 0.80)
    d.text((W // 2, y), "THE END", font=FONT_BIG.font_variant(size=int(150 * (1.3 - 0.3 * k))), anchor="mm",
           fill=(255, 40, 40), stroke_width=10, stroke_fill=(0, 0, 0))
    d.text((W // 2, y + 140), "thanks for watching", font=FONT.font_variant(size=54), anchor="mm",
           fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    return fr


_plan_clip_offsets()


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
