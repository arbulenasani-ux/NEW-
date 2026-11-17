#!/usr/bin/env python3
"""Procedural sound design (no paid APIs): creepy music-box bed, drones, wind,
clock ticks, 3 knocks, heartbeat, whooshes, impacts, silence before the twist.
Writes assets/audio/music_sfx.wav (48 kHz stereo) and the final mix.wav."""
import os, json, subprocess
import numpy as np, soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUD = os.path.join(ROOT, "assets", "audio")
SR, T = 48000, 61.0
N = int(SR * T)
rng = np.random.default_rng(217)
SUBS = json.load(open(os.path.join(AUD, "timings.json")))["subs"]
S = lambda i: SUBS[i][0]   # start of sentence i
E_ = lambda i: SUBS[i][1]  # end of sentence i
KNOCKS = (23.25, 23.65, 24.05)   # from inside the closet (gap before "Three knocks")
END_KNOCKS = (59.0, 59.45, 59.9)
t = np.arange(N) / SR


def at(sec):
    return int(sec * SR)


def add(buf, sig, sec, gain=1.0):
    s = at(sec)
    e = min(s + len(sig), len(buf))
    if e > s:
        buf[s:e] += sig[: e - s] * gain


def lp(x, fc):  # one-pole low-pass
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y


def lp_fast(x, fc):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, fc, "low", fs=SR, output="sos"), x)


def hp_fast(x, fc):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, fc, "high", fs=SR, output="sos"), x)


def bp_fast(x, lo, hi):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def reverb(x, decay=1.8, mix=0.35):
    ir_len = int(decay * SR)
    ir = rng.standard_normal(ir_len) * np.exp(-np.linspace(0, 7, ir_len))
    ir = lp_fast(ir, 5000); ir /= np.abs(ir).sum() ** 0.5 * 6
    from scipy.signal import fftconvolve
    wet = fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix * 3


def env_ad(n, a, d):
    e = np.ones(n)
    na = max(int(a * SR), 1)
    e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.arange(n - na) / (d * SR))
    return e


# ---------------- music bed ----------------
music = np.zeros(N)
# drone (A1 / E2 detuned) with slow swell
drone = (np.sin(2 * np.pi * 55 * t) + 0.8 * np.sin(2 * np.pi * 55.35 * t)
         + 0.5 * np.sin(2 * np.pi * 82.4 * t) + 0.25 * np.sin(2 * np.pi * 110.6 * t))
drone *= 0.55 + 0.45 * np.sin(2 * np.pi * t / 9.0) ** 2
music += 0.10 * drone
# music box melody (A minor, slightly detuned, like an old toy)
notes = {"A4": 440, "C5": 523.25, "E5": 659.25, "D5": 587.33, "B4": 493.88, "G4": 392, "F5": 698.46, "E4": 329.63}
seq = ["A4", "C5", "E5", "C5", "D5", "B4", "G4", "B4", "A4", "C5", "E5", "F5", "E5", "C5", "B4", "E4"]
box = np.zeros(N)
step = 0.42
k = 0
tt = 0.0
while tt < T:
    f = notes[seq[k % len(seq)]] * (1 + 0.004 * rng.standard_normal())
    n = int(1.6 * SR)
    x = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * 2 * f * x) + 0.12 * np.sin(2 * np.pi * 3.01 * f * x))
    add(box, tone * env_ad(n, 0.003, 0.35), tt, 0.16)
    k += 1; tt += step
box = reverb(box, 2.2, 0.45)
music += box
# wind / air
wind = lp_fast(rng.standard_normal(N), 700) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 6.3 + 1) ** 2)
music += 0.05 * wind / np.abs(wind).max()

# music envelope per section: quiet under voice, cut before the twist
g = np.ones(N)
def ramp(s0, s1, v0, v1):
    a, b = at(s0), at(s1)
    g[a:b] = np.linspace(v0, v1, b - a)
def hold(s0, s1, v):
    g[at(s0):at(s1)] = v
hold(0, S(11) - 0.2, 1.0)
ramp(S(11) - 0.2, S(11), 1.0, 0.35)                  # footsteps / silence under the bed
hold(S(11), S(14), 0.25)
ramp(S(13) + 0.2, S(13) + 0.6, 0.25, 0.0)            # dead silence before the knocks
hold(S(13) + 0.6, S(16), 0.0)
ramp(S(16), S(16) + 0.4, 0.0, 0.7)
hold(S(16) + 0.4, S(22), 0.7)
ramp(S(22), S(22) + 0.2, 0.7, 1.1)                   # escape: full intensity
hold(S(22) + 0.2, S(29), 1.1)
ramp(S(29), S(29) + 0.3, 1.1, 0.5)
hold(S(29) + 0.3, E_(31), 0.5)
ramp(E_(31), E_(31) + 0.2, 0.5, 0.0)                 # silence before the cliffhanger
hold(E_(31) + 0.2, S(32) - 0.05, 0.0)
ramp(S(32) - 0.05, S(32) + 0.2, 0.0, 1.0)
hold(S(32) + 0.2, END_KNOCKS[0] - 0.2, 1.0)
ramp(END_KNOCKS[0] - 0.2, END_KNOCKS[0], 1.0, 0.2)
hold(END_KNOCKS[0], 61.0, 0.2)
music *= g

# ---------------- SFX ----------------
sfx = np.zeros(N)


def knock(sec, gain=1.0):
    n = int(0.35 * SR); x = np.arange(n) / SR
    body = np.sin(2 * np.pi * (140 * np.exp(-x * 9) + 70) * x) * np.exp(-x * 26)
    click = bp_fast(rng.standard_normal(n), 400, 2500) * np.exp(-x * 120) * 0.6
    wood = np.sin(2 * np.pi * 420 * x) * np.exp(-x * 45) * 0.35
    s = body + click + wood
    add(sfx, reverb(s / np.abs(s).max(), 0.7, 0.25), sec, 0.9 * gain)


def tick(sec, gain=0.22, hi=True):
    n = int(0.05 * SR); x = np.arange(n) / SR
    s = bp_fast(rng.standard_normal(n), 2500 if hi else 1600, 7000) * np.exp(-x * 220)
    add(sfx, s / np.abs(s).max(), sec, gain)


def heart(sec, gain=0.5):
    for off, a in ((0, 1.0), (0.17, 0.7)):
        n = int(0.22 * SR); x = np.arange(n) / SR
        s = np.sin(2 * np.pi * (60 * np.exp(-x * 4)) * x) * np.exp(-x * 18)
        add(sfx, s, sec + off, gain * a)


def impact(sec, gain=0.9, length=2.5):
    n = int(length * SR); x = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (48 * np.exp(-x * 1.3) + 28) * x) * np.exp(-x * 2.2)
    crack = lp_fast(rng.standard_normal(n), 3000) * np.exp(-x * 14) * 0.5
    s = sub + crack
    add(sfx, reverb(s / np.abs(s).max(), 2.0, 0.3), sec, gain)


def whoosh(sec, gain=0.35, length=0.6):
    n = int(length * SR); x = np.linspace(0, 1, n)
    s = rng.standard_normal(n)
    s = bp_fast(s, 300, 3500) * np.sin(np.pi * x) ** 2
    add(sfx, s / np.abs(s).max(), sec - length * 0.6, gain)


def riser(s0, s1, gain=0.35):
    n = at(s1) - at(s0); x = np.linspace(0, 1, n)
    f = 200 + 1800 * x ** 2
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = (0.6 * np.sin(ph) + 0.4 * hp_fast(rng.standard_normal(n), 1500) * x) * x ** 1.5
    add(sfx, s, s0, gain)


def sting(sec, gain=0.45):  # dissonant violin-ish screech
    n = int(1.4 * SR); x = np.arange(n) / SR
    s = sum(np.sign(np.sin(2 * np.pi * f * x + 0.3 * np.sin(2 * np.pi * 6 * x))) for f in (740, 784, 1046))
    s = lp_fast(s, 3500) * env_ad(n, 0.02, 0.5)
    add(sfx, reverb(s / np.abs(s).max(), 1.6, 0.4), sec, gain)


impact(0.0, 0.8)                                         # hook hit
whoosh(S(2), 0.3)
for s_ in np.arange(S(4), S(6), 1.0):                     # clock ticks at 2:16
    tick(s_, 0.22)
sting(S(5), 0.3)                                          # staring at my door
whoosh(S(6), 0.3)
impact(S(8) + 0.2, 0.5, 1.5)                              # the note
whoosh(S(9), 0.3)
# door creak (filtered noise sweep) + footsteps
n = int(1.4 * SR); x = np.linspace(0, 1, n)
creak = bp_fast(rng.standard_normal(n), 600, 1800) * (0.4 + 0.6 * np.sin(2 * np.pi * 7 * x) ** 2) * np.sin(np.pi * x)
add(sfx, creak / np.abs(creak).max(), S(10), 0.35)
for s_ in (S(11), S(11) + 0.45, S(11) + 0.9):
    heart(s_, 0.35)                                        # heavy footsteps (low thumps)
for s_ in KNOCKS:                                          # THREE KNOCKS from the closet
    knock(s_)
for s_ in np.arange(S(16), S(22), 0.85):                   # slow heartbeat
    heart(s_, 0.4)
tick(S(21) + 0.6, 0.35); tick(S(21) + 1.1, 0.3)           # one minute left
whoosh(S(22), 0.45); impact(S(22), 0.6, 1.5)              # run!
bpm, s_ = 110.0, S(22) + 0.4
while s_ < S(29):
    heart(s_, 0.5); s_ += 60 / bpm; bpm = min(bpm + 2, 140)
sting(S(24) + 0.2, 0.5); impact(S(24) + 0.2, 0.8)         # Mom's face... too wide
whoosh(S(26), 0.35)
sting(S(27) + 0.5, 0.35)                                  # glowing eyes
riser(E_(31) - 2.5, E_(31), 0.3)
impact(S(34) + 0.25, 1.0, 3.0); sting(S(34) + 0.25, 0.5)  # "...wasn't me."
for s_ in END_KNOCKS:                                     # knocks -> PART 3
    knock(s_, 1.1)

# room tone so the silence isn't digital black
room = lp_fast(rng.standard_normal(N), 400) * 0.004

bed = music * 0.5 + sfx * 0.75 + room
bed = np.stack([bed, bed], 1)
# tiny stereo widening for the music box
bed[:, 0] += np.roll(box * g, 300) * 0.08
bed[:, 1] += np.roll(box * g, -300) * 0.08
bed /= np.abs(bed).max() / 0.9
sf.write(os.path.join(AUD, "music_sfx.wav"), bed.astype(np.float32), SR, subtype="PCM_24")
print("music_sfx.wav written")
