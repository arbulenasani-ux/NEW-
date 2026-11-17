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
    (0.00, 1, 1.10, 1.30, (.50, .58), (.50, .55), "night"),     # the monsters aren't outside (P1 eyes)
    (S(1), 2, 1.05, 1.30, (.50, .50), (.50, .50), "night"),     # found out the hard way (P1 yard)
    (S(2), 3, 1.00, 1.15, (.45, .55), (.48, .50), "day"),       # mom acting strange
    (S(3), 3, 1.90, 2.10, (.60, .38), (.60, .36), "day"),       # she never sleeps
    (S(4), 4, 1.00, 1.30, (.50, .55), (.50, .50), "night"),     # at 2:16 in the hallway
    (S(5), 5, 1.05, 1.30, (.62, .45), (.62, .42), "night"),     # staring at my door
    (S(6), 5, 1.30, 1.45, (.55, .72), (.55, .70), "night"),     # note under my pillow (Alex in bed)
    (S(7), 6, 1.05, 1.20, (.50, .50), (.50, .48), "night"),     # in my own handwriting
    (S(8), 6, 1.12, 1.25, (.50, .47), (.50, .47), "night"),     # DON'T LET HER SEE YOU LOOKING
    (S(9), 7, 1.00, 1.20, (.50, .60), (.50, .60), "night"),     # hid under my bed
    (S(10), 7, 1.30, 1.50, (.55, .45), (.55, .42), "night"),    # door creaked open
    (S(11), 7, 1.80, 2.00, (.62, .52), (.62, .52), "night"),    # footsteps
    (S(12), 8, 1.05, 1.25, (.65, .50), (.65, .48), "night"),    # silence... knocks from the closet
    (S(14), 8, 1.40, 1.60, (.70, .45), (.70, .45), "night"),    # three knocks, inside my closet
    (S(16), 9, 1.00, 1.25, (.45, .45), (.40, .40), "night"),    # Alex... it's me
    (S(19), 2, 1.30, 1.70, (.50, .52), (.50, .50), "night"),    # the woman from the yard
    (S(20), 9, 1.50, 1.75, (.35, .38), (.35, .36), "night"),    # switched places at 2:17
    (S(21), 10, 1.40, 1.85, (.53, .64), (.53, .64), "red"),     # one minute left (2:17 clock)
    (S(22), 11, 1.00, 1.20, (.50, .55), (.50, .55), "night"),   # we ran for the stairs
    (S(23), 12, 1.00, 1.15, (.50, .50), (.50, .48), "night"),   # the thing turned around
    (S(24), 12, 1.30, 1.45, (.50, .45), (.50, .45), "night"),   # it had Mom's face
    (S(25), 12, 1.70, 1.95, (.50, .55), (.50, .56), "night"),   # smile way too wide
    (S(26), 13, 1.00, 1.20, (.50, .58), (.50, .58), "night"),   # we made it outside
    (S(27), 1, 1.05, 1.30, (.50, .45), (.50, .42), "night"),    # every window: glowing eyes
    (S(28), 13, 1.50, 1.70, (.45, .60), (.45, .60), "night"),   # watching us
    (S(29), 14, 1.00, 1.20, (.50, .55), (.50, .52), "night"),   # squeezed my hand, whispered
    (S(30), 14, 1.50, 1.70, (.38, .40), (.38, .38), "night"),   # whatever you do...
    (S(31), 14, 1.85, 2.10, (.40, .35), (.40, .34), "night"),   # don't look at your reflection
    (S(32), 15, 1.00, 1.25, (.50, .45), (.50, .40), "night"),   # looked down at the puddle
    (S(33), 16, 1.00, 1.30, (.50, .45), (.50, .42), "night"),   # the boy in the reflection
    (S(34), 16, 1.40, 1.55, (.56, .36), (.57, .36), "night"),   # ...wasn't me
]
# only the usable start of some clips (later frames drift: figures fade into fog / face changes)
CLIP_MAXT = {1: 1.6, 12: 2.4, 15: 1.3}


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


PRECROP = {10: (0.0, 0.0, 0.78, 0.775), 6: (0.15, 0.15, 0.85, 0.70)}
END_CARD = 58.2
BURN_CAPTIONS = False   # captions are added inside TikTok by the creator   # "PART 3" + knocks

# events: (time, kind, strength)
EVENTS = [(0.0, "flash", 0.6), (S(8) + 0.2, "flash", 0.3),
          (23.25, "shake", 1.0), (23.65, "shake", 1.0), (24.05, "shake", 1.0),
          (S(21), "flash_red", 0.6), (S(22), "shake", 0.8), (S(24) + 0.2, "flash", 0.6), (S(24) + 0.2, "shake", 1.0),
          (S(27) + 0.5, "flash", 0.3), (S(34) + 0.25, "flash", 0.9), (S(34) + 0.25, "shake", 1.2),
          (59.0, "shake", 0.9), (59.45, "shake", 0.9), (59.9, "shake", 0.9)]


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
    if cf is not None and z0 < 1.9:   # animation already moves -> gentler digital zoom (keeps it sharp)
        z = max(1.0 + (z - 1.0) * 0.45, 1.03)
    im = cf or src(idx)
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
    y = int(H * 0.80)
    d.text((W // 2, y), "PART 3", font=FONT_BIG.font_variant(size=int(150 * (1.3 - 0.3 * k))), anchor="mm",
           fill=(255, 40, 40), stroke_width=10, stroke_fill=(0, 0, 0))
    d.text((W // 2, y + 140), "follow so you don't miss it", font=FONT.font_variant(size=54), anchor="mm",
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
