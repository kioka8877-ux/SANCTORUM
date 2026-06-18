import os, json, sys, base64
import urllib.request
from pydub import AudioSegment

PROJECT_ID = os.environ["PROJECT_ID"]
TOKEN = os.environ["GH_PAT"]
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
        print(f"  [!] chunk_{i}: manquant ou vide — skip")

if found == 0:
    print("[ECHEC] Aucun chunk audio trouve")
    sys.exit(1)

dur = len(combined) / 1000
print(f"[CONCAT] {found} chunks — {dur:.1f}s total")
combined.export(output_mp3, format="mp3", bitrate="192k")
sz = os.path.getsize(output_mp3)
print(f"[CONCAT] {output_mp3} — {sz / 1024:.0f} KB")

dest = f"F02_LACERAT/IN/voice_{PROJECT_ID}.mp3"
url = f"https://api.github.com/repos/kioka8877-ux/ANGRON-V2/contents/{dest}"
headers = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}

sha = None
try:
    req = urllib.request.Request(url, headers={"Authorization": f"token {TOKEN}"})
    with urllib.request.urlopen(req) as r:
        sha = json.load(r)["sha"]
except Exception:
    pass

with open(output_mp3, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

payload = {
    "message": f"[DOMINION] voice_{PROJECT_ID}.mp3 — {dur:.1f}s audio",
    "content": b64,
}
if sha:
    payload["sha"] = sha

req2 = urllib.request.Request(
    url, data=json.dumps(payload).encode(), method="PUT", headers=headers
)
with urllib.request.urlopen(req2) as r:
    commit = json.load(r)["commit"]["sha"][:8]

print(f"[PUSH] ANGRON-V2 {dest} — commit {commit}")
print(f"[DOMINION] COMPLETE — voice_{PROJECT_ID}.mp3 disponible")
