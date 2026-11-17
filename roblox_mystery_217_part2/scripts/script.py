"""PART 2 - English narration (all video content is English).

BLOCKS: (block_id, voice, text, anchor_start_or_None, pause_after_s)
N = narrator Alex (Higgsfield/ElevenLabs "Dylan"), W = real mom whispering (ElevenLabs "Faye")
"""

VOICE_IDS = {
    "N": "b847bc29-f184-583a-8ad9-d1f1e16d1a60",   # Dylan
    "W": "d198dc0b-c4e5-5198-aa1d-ecf5ca0927c4",   # Faye
    "M": "d198dc0b-c4e5-5198-aa1d-ecf5ca0927c4",
}

BLOCKS = [
    # 0-12s HOOK + creepy mom
    (401, "N", "In this town, the monsters aren't outside. I found that out the hard way. After that night, Mom started acting strange. "
               "She never sleeps. And every night at 2:16, she stands in the hallway... staring at my door.", 0.05, 0.45),
    # 12-18s the note
    (402, "N", "Then I found a note under my pillow. In my own handwriting. It said: Don't let her see you looking.", None, 0.6),
    # 18-25s hiding
    (403, "N", "That night, I hid under my bed. The door creaked open. Footsteps. Then... silence.", None, 1.6),
    # knocks SFX in the gap before 404 (set in build_sfx.py)
    (404, "N", "Three knocks. From inside my closet.", None, 0.7),
    (405, "W", "Alex... it's me. Your real mom.", None, 0.25),
    (406, "N", "It was the woman from the yard. She said they switched places at 2:17. And we had one minute left.", None, 0.35),
    # escape
    (407, "N", "We ran for the stairs. The thing in the hallway slowly turned around. It had Mom's face... but its smile was way too wide. "
               "We made it outside. But every window on the street was full of glowing eyes. Watching us.", None, 0.45),
    (408, "N", "Then she squeezed my hand and whispered...", None, 0.15),
    (409, "W", "Whatever you do... don't look at your reflection.", None, 0.95),
    # cliffhanger
    (410, "N", "I looked down at the puddle. The boy in the reflection... wasn't me.", None, 0.0),
]

RED = set()
YELLOW = set()
