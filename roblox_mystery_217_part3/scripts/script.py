"""PART 3 (FINAL) - English narration (all video content is English).

BLOCKS: (block_id, voice, text, anchor_start_or_None, pause_after_s)
N = narrator Alex (Higgsfield/ElevenLabs "Dylan"), W = real mom (ElevenLabs "Faye", whisper processing)
"""

VOICE_IDS = {
    "N": "b847bc29-f184-583a-8ad9-d1f1e16d1a60",   # Dylan
    "W": "d198dc0b-c4e5-5198-aa1d-ecf5ca0927c4",   # Faye
    "M": "d198dc0b-c4e5-5198-aa1d-ecf5ca0927c4",
}

BLOCKS = [
    (501, "N", "In this town, never trust your reflection. The boy in the puddle smiled at me. But I wasn't smiling.", 0.05, 0.6),
    (502, "W", "Don't look at him, Alex. That thing wants your place.", None, 0.7),
    (503, "N", "Then Mom told me the truth. Every night at 2:17, the things inside the houses look out the windows. "
               "And if you look back... they take your place.", None, 0.6),
    (504, "N", "That's why the people outside looked so scared. They weren't the monsters. They were the real families. "
               "Locked out of their own homes. Mom has been outside for three years.", None, 0.6),
    (506, "N", "She said there was only one way back inside. Make your reflection look away first. Before the clock hits 2:18.", None, 0.6),
    (507, "N", "So I stared at him. He stared at me. Ten seconds. Twenty. Then the church bell rang.", None, 1.0),
    (508, "N", "He blinked.", None, 1.2),
    (509, "N", "The puddle went dark. And every window on the street went black.", None, 0.7),
    (510, "N", "When I opened my eyes, I was in my room. And my real mom was holding my hand.", None, 0.6),
    (511, "N", "That morning, the people outside finally went home.", None, 0.9),
    (512, "N", "So now, this town has a new rule. At 2:17 AM... if something looks at you through the window... don't look away.", None, 0.0),
]

RED = set()
YELLOW = set()
