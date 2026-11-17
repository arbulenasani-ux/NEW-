"""Single source of truth for the English narration (all video content is English).

BLOCKS: (block_id, voice, text, anchor_start_or_None, pause_after_s)
voice: N = narrator Alex (first person, "In this town..." format) - Higgsfield ElevenLabs preset "Dylan"
       M = mom calling from outside (processed: distant / reverb)
       W = real mom whispering behind Alex (processed: close / whisper)
Each block is one TTS take; anchors pin blocks to the story timeline.
"""

VOICE_IDS = {
    "N": "b847bc29-f184-583a-8ad9-d1f1e16d1a60",   # Dylan
    "M": None, "W": None,                          # filled after casting (see README)
}

BLOCKS = [
    # 0-10s  HOOK + RULE
    (201, "N", "In this town, nobody is allowed to look outside at exactly 2:17 AM. Nobody knows who made the rule. "
               "Nobody ever explains why. At 2:16, every curtain closes. And every light goes out.", 0.05, 0.15),
    # 10-18s ALEX
    (202, "N", "My name is Alex. And I always thought it was just a story to scare kids. Until last night. "
               "I was almost asleep... when I heard it.", None, 0.0),
    # 17-27s KNOCKS (SFX at 17.25 / 17.7 / 18.15) + CLOCK
    (203, "N", "Three knocks. On my window. I checked the clock.", 18.75, 0.45),
    (204, "N", "Two seventeen. A.M.", 22.85, 0.2),
    # 27-37s MOM OUTSIDE
    (205, "N", "Then I heard my mom's voice. From outside.", None, 0.15),
    (301, "M", "Alex... please... let me in.", None, 0.3),
    (206, "N", "I looked. She was standing in the yard. Smiling. Same sweater. Same smile. But she didn't blink. Not once.", None, 0.0),
    # 37-45s REAL MOM
    (207, "N", "Then a hand grabbed my shoulder. My real mom was standing behind me.", None, 0.1),
    (302, "W", "Don't look at her.", None, 0.15),
    (208, "N", "I turned back. But she was still there.", None, 0.0),
    # 45-53s MORNING REVEAL
    (209, "N", "The next morning, I looked outside. In front of every single house, someone was standing. "
               "Staring into the windows. And every single one of them... looked terrified.", None, 0.75),
    # 53-60s TWIST (music cuts to silence right before)
    (210, "N", "The rule was never protecting us from them. It was protecting them... from us.", None, 0.0),
]

# words shown in red / yellow if captions are ever burned in (off by default: captions are added in TikTok)
RED = {"blink.", "terrified.", "2:17", "AM", "AM.", "2:16,", "never", "us.", "us", "real", "knocks.", "Don't", "her."}
YELLOW = {"rule.", "rule", "mom's", "smiling.", "every", "single", "them", "staring", "window."}
