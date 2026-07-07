import os, sys
from pydub import AudioSegment

PROJECT_ID = os.environ.get("PROJECT_ID", "custom")
N = int(os.environ.get("N_WORKERS", "10"))
output_mp3 = f"/tmp/voice_{PROJECT_ID}.mp3"

combined = AudioSegment.empty()
found = 0
for i in range(N):
    path = f"/tmp/chunk_{i}.wav"
    if os.path.exists(path) and os.path.getsize(path) > 0:
        seg = AudioSegment.from_wav(path)
        combined += seg
        print(f"  [+] chunk_{i}: {len(seg) / 1000:.1f}s")
        found += 1
    else:
        print(f"  [!] chunk_{i}: manquant ou vide - skip")

if found == 0:
    print("[ECHEC] Aucun chunk audio trouve")
    sys.exit(1)

dur = len(combined) / 1000
print(f"[CONCAT] {found} chunks - {dur:.1f}s total")
combined.export(output_mp3, format="mp3", bitrate="192k")
sz = os.path.getsize(output_mp3)
print(f"[CONCAT] {output_mp3} - {sz / 1024:.0f} KB")
print(f"[DOMINION] COMPLETE - voice_{PROJECT_ID}.mp3 pret ({dur:.1f}s)")
