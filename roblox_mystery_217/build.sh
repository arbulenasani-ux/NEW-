#!/usr/bin/env bash
# Full local rebuild (no credits): voice assembly -> sound design -> edit -> mix -> encode -> thumbnail
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/build_voice.py          # Higgsfield takes in assets/audio/vo -> voiceover.wav + SRT
python3 scripts/build_sfx.py            # music box, drones, knocks, ticks, heartbeat, impacts
python3 scripts/edit.py                 # stills -> moving 1080x1920 30fps video
ffmpeg -v error -y -i assets/audio/voiceover.wav -i assets/audio/music_sfx.wav -filter_complex \
 "[0:a]aformat=channel_layouts=stereo,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,equalizer=f=3000:t=q:w=1:g=2,asplit=2[v][sc];[1:a][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[bed];[v][bed]amix=inputs=2:weights='1 0.9':normalize=0,atrim=0:60,loudnorm=I=-14:TP=-1.0:LRA=9[out]" \
 -map "[out]" -ar 48000 -c:a pcm_s24le assets/audio/final_mix.wav
cd output
ffmpeg -v error -y -i _video_noaudio.mp4 -c:v libx264 -preset slow -b:v 7M -pass 1 -an -f null /dev/null
ffmpeg -v error -y -i _video_noaudio.mp4 -i ../assets/audio/final_mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow \
 -b:v 7M -maxrate 10M -bufsize 14M -pass 2 -pix_fmt yuv420p -profile:v high -c:a aac -b:a 256k -t 60 -movflags +faststart \
 This_Town_Has_One_Rule_217AM.mp4
rm -f ffmpeg2pass* _video_noaudio.mp4
ffmpeg -v error -y -i ../assets/audio/voiceover.wav -c:a libmp3lame -b:a 192k voiceover_en.mp3
cp ../assets/audio/voiceover.wav voiceover_en.wav
cd .. && python3 scripts/thumbnail.py
echo "done -> output/"
