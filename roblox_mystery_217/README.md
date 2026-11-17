# This Town Has One Rule Nobody Understands… (Roblox-Mystery-TikTok, 61 s)

Fertiges virales Roblox-Horror-Video, aufgebaut wie das Referenzformat „In this town…“ (Ich-Erzähler, Roblox-Szenen, schnelle Schnitte etwa alle 1,5 s, leise Musik unter der Stimme), aber mit eigener Story. **Alle Inhalte im Video sind auf Englisch (US).**

## Fertige Dateien (`output/`)

| Datei | Inhalt |
|---|---|
| `This_Town_Has_One_Rule_217AM.mp4` | Finales Video: 1080×1920, 9:16, 30 fps, **exakt 61,000 s**, H.264 Main@4.0 (öffnet sich auf jedem Handy) + AAC, −14 LUFS, **alle Szenen animiert** |
| `voiceover_en.mp3` / `voiceover_en.wav` | Englischer Voiceover (nur Stimme, ohne Musik) |
| `voiceover_en.srt` | Englische Untertitel (optional, die Untertitel kommen in TikTok dazu, im Video ist nichts eingebrannt) |
| `thumbnail_never_look_outside_217am.png` | Thumbnail „NEVER LOOK OUTSIDE AT 2:17 AM“ |

## Ablauf (Zeitplan)

| Zeit | Szene |
|---|---|
| 0–4 s | Hook: „In this town, nobody is allowed to look outside at exactly 2:17 AM.“ + kurzer Blick auf die Uhr |
| 4–10 s | Regel, Vorhänge schließen sich, alle Lichter gehen aus |
| 10–17 s | Alex (Tag → Nacht im Bett) |
| 17–22 s | Drei Klopfer (Kamerawackler + SFX), Uhr zeigt 2:17 AM |
| 22–36 s | Stimme der Mutter von draußen, sie steht im Garten und lächelt und blinzelt nicht |
| 37–44 s | Hand auf der Schulter: die echte Mutter flüstert „Don't look at her.“ |
| 44–53 s | Morgen: vor jedem Haus steht jemand, und alle sehen panisch aus (Hinweis auf den Twist) |
| 53,5 s | Stille |
| 54–58,5 s | Twist: „It was protecting them… from us.“ Alex mit leuchtenden Augen |
| 58,5–61 s | „PART 2“ + erneut drei Klopfer (Cliffhanger) |

## Kosten (Higgsfield-Credits): gesamt **155,65** (Kontostand 1004,12 → 848,47)

| Posten | Credits |
|---|---|
| 24 Bilder Nano Banana Pro 2K (inklusive Charakterblatt und 1 Nachbesserung) | ≈ 48 |
| Stimmen ElevenLabs (Erzähler Dylan, Mom Faye, inklusive Stimm-Casting) | ≈ 5 |
| 20 Animationen Kling 3.0 std ohne Ton (15× 3 s à 4,5, 5× 5 s à 7,5) | ≈ 105 |

Kostenlos und lokal: Sounddesign, Musik, Schnitt, Kamerabewegung, Mix, Export, Thumbnail.

## Projektstruktur

```
assets/hf/          Higgsfield-Standbilder (+ Charakterblatt), jobs.json = Herkunft
assets/clips/       20 Kling-Animationen (NN.mp4), clips.json = Herkunft; fetch_clips.py extrahiert Frames
assets/audio/vo/    Higgsfield-Sprachtakes je Block (201–210 Erzähler, 301/302 Mutter)
assets/audio/casting/  Stimmproben (Benji, Dylan, Evan, Faye, Celine)
assets/fonts/       Poppins (OFL) für End-Card und Thumbnail
scripts/script.py   Englisches Skript + Zeitanker (Single Source of Truth)
scripts/build_voice.py  Takes schneiden, Pausen straffen, Tempo ×1.12, platzieren, SRT
scripts/build_sfx.py    Spieluhr-Musik, Drone, Wind, Ticken, 3 Klopfer, Herzschlag, Impacts, Stille
scripts/edit.py         Shotliste (an die Stimme gekoppelt) → Frames → FFmpeg
scripts/thumbnail.py    Thumbnail
build.sh            Kompletter Neuaufbau ohne Credits
```

Neu bauen: `./build.sh` (benötigt `ffmpeg`, `python3`, `numpy`, `scipy`, `pillow`, `soundfile`).

## Qualitätskontrolle (bestanden)

- Länge exakt 61,000 s, 1830 Frames, 1080×1920 bei 30 fps, H.264 Main@4.0
- Keine schwarzen Frames (`blackdetect`)
- Lautheit −14,2 LUFS integriert, True Peak −0,9 dBFS, kein Clipping
- Einzige Stille ist die gewollte Pause vor dem Twist (53,55–54,12 s)
- Musik liegt beim Sprechen etwa 15 dB unter der Stimme (Ducking)
- Komplett englisch; keine eingebrannten Untertitel (die kommen in TikTok dazu)
