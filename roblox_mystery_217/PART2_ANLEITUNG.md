# Anleitung für Part 2 (und jedes weitere „In this town…“-Video)

So ist Part 1 entstanden. Für Part 2 genau diese Schritte wiederholen, damit Stil, Stimmen, Qualität und Kosten gleich bleiben.

## 0. Vorgaben

- Format wie die Referenz „In this town…“ (TikTok @in.this.world.stories): Ich-Erzähler, Roblox-Szenen, Schnitt etwa alle 1,5–2,5 s, leise Musik unter der Stimme
- Alles im Video auf **Englisch (US)**; Chat mit dem Nutzer auf **Deutsch**
- **Keine eingebrannten Untertitel**: Die macht der Nutzer in TikTok. Eine SRT-Datei wird trotzdem mitgeliefert.
- Länge: **61 s** (1:01), 1080×1920, 30 fps
- Jede Szene ist **animiert** (Kling-Clip). Nur Szenen mit wichtigem Text (z. B. die Uhr „2:17 AM“) bleiben Standbild mit Kamerafahrt, weil die KI Ziffern verfälscht.
- Bilder, Ton und Stimme müssen synchron laufen. Die Shotliste hängt an den echten Satzzeiten (`S(i)` aus `timings.json`).

## 1. Skript (kostenlos)

- `scripts/script.py`: Story in **Blöcken** (1 Block = 1 Sprach-Take), mit Zeitankern für die Schlüsselmomente
- Nach dem Hook alle 2–3 s eine neue Information, dazu kleine Hinweise auf den Twist, eine Pause vor dem Twist und am Ende ein Cliffhanger („PART 3“ + Klopfen)

## 2. Bilder: Higgsfield, `nano_banana_pro`, 2K, 9:16 (2 Credits pro Bild)

- Zuerst die Anker: Charakterblatt (Alex + Mom) und die Stadt-Szene. Danach jedes Bild mit `image_references` auf diese Job-IDs.
  - Charakterblatt Part 1: `838ffe7c-2f33-4358-a8e9-528751a9b4f6`
  - Stadt nachts: `d1ff9092-a924-4651-a036-8897a2e79961`
- Prompt-Präfix: „Roblox game screenshot rendered in Roblox Studio with future lighting … vertical 9:16 … No text, no UI.“
- Rate-Limit: höchstens **4 gleichzeitig**. Abgelehnte Aufträge (429) kosten nichts, später einfach nochmal schicken.
- Fehler lokal reparieren statt neu zu würfeln (z. B. Editor-UI am Rand wegschneiden über `PRECROP` in `edit.py`)

## 3. Animation: Higgsfield `kling3_0`, Modus `std`, `sound: off`, 9:16

- 3 s = 4,5 Credits, 5 s = 7,5 Credits. 5 s nur für Bilder, die mehrfach oder lange gezeigt werden.
- `medias: [{value: <Bild-Job-ID>, role: start_image}]`
- Der Prompt beschreibt genau die Aktion, die der Erzähler in dem Moment sagt. Immer anhängen: „Keep blocky Roblox style, no morphing“.
- Download: Job-URLs in `assets/clips/clips.json` eintragen, dann `python3 scripts/fetch_clips.py` (extrahiert die Frames)

## 4. Stimme: Higgsfield `text2speech_v2`, Variante `elevenlabs` (≈0,3 Credits pro Satz)

- Erzähler **Dylan**: `b847bc29-f184-583a-8ad9-d1f1e16d1a60` (jung, US, ~174 Hz, ausdrucksstark)
- Mom **Faye**: `d198dc0b-c4e5-5198-aa1d-ecf5ca0927c4` (warm). Draußen bekommt die Stimme Hall und Tiefpass, das Flüstern einen Höhenboost (`build_voice.py`).
- Takes nach `assets/audio/vo/<block>.mp3`
- `build_voice.py`: Pausen auf 0,18 s straffen, Tempo ×1,12, auf die Anker setzen. Erzeugt `timings.json` und SRT.

## 5. Ton, Schnitt, Export (kostenlos, lokal)

```
./build.sh
```

- `build_sfx.py`: Spieluhr-Musik, Drone, Wind, Ticken, Klopfer, Herzschlag, Impacts, Stille vor dem Twist. Alle Zeiten hängen an `S(i)`.
- `edit.py`: Shotliste `SHOTS` mit `S(i)`-Zeiten. Clips laufen weiter, wenn ein Bild mehrfach vorkommt.
- Mix: Ducking, Musik etwa 15 dB unter der Stimme, −14 LUFS, True Peak −1 dBFS
- Export: H.264 **Main@4.0**, ~5 Mbit/s, AAC, `+faststart`. So öffnet sich die Datei auf jedem Handy. Die alte Version mit High@5.0 und 54 MB ließ sich beim Nutzer nicht öffnen.

## 6. Qualitätskontrolle vor der Abgabe

- `ffprobe`: Dauer genau 61,000 s, 1830 Frames, 1080×1920
- `blackdetect`: keine schwarzen Frames
- `ebur128`: etwa −14 LUFS, kein Clipping
- `silencedetect`: Stille nur dort, wo sie gewollt ist
- Kontaktbogen der fertigen MP4 ansehen: Passt jede Szene zum gesprochenen Satz?

## Kosten Part 1 (Richtwert für Part 2)

**155,65 Credits** gesamt: Bilder ≈48, Stimmen ≈5, Animationen ≈105 (inklusive 2 Testclips).
Sparen: Testclips nur bei neuen Prompt-Arten; 3-s-Clips statt 5 s wo möglich; Clips mehrfach nutzen (Ausschnitt/Zoom variieren).

## Bekannte Fallen
- Kling verändert Ziffern und Text, deshalb die Uhr als Standbild lassen.
- Am Clip-Ende passieren manchmal Fehler: Figuren lösen sich im Nebel auf, Gesichter wechseln, Artefakte um den Mond. Dann über `CLIP_MAXT` in `edit.py` nur den Anfang nutzen.
- Clips sind 716×1284. Starkes digitales Zoomen (>2×) wird unscharf.
- Higgsfield-CDN `d8j0ntlcm91z4.cloudfront.net` muss in der Cloud-Umgebung freigegeben sein (ist erledigt).
