import os, json, sys, time, subprocess, wave, struct
from huggingface_hub import snapshot_download

CHUNK_ID = os.environ["CHUNK_ID"]
REF_AUDIO = os.environ.get("REF_AUDIO", "")
output_path = f"/tmp/chunk_{CHUNK_ID}.wav"

with open("/tmp/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

text = chunks.get(str(CHUNK_ID), "").strip()

if not text:
    print(f"[WORKER {CHUNK_ID}] Chunk vide — fichier silence")
    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        wf.writeframes(struct.pack("<h", 0) * 2205)
    sys.exit(0)

print(f"[WORKER {CHUNK_ID}] {len(text)} chars : {text[:80]}...")

t0 = time.time()
snapshot_download(repo_id="k2-fsa/OmniVoice", local_dir="/tmp/omnivoice_model")
print(f"[MODEL] {time.time() - t0:.1f}s — pret")

cmd = [
    "omnivoice-infer",
    "--model", "/tmp/omnivoice_model",
    "--text", text,
    "--output", output_path,
]
if REF_AUDIO and os.path.exists(REF_AUDIO):
    cmd += ["--ref_audio", REF_AUDIO]
    print(f"[MODE] voice_clone")
else:
    print("[MODE] auto_voice")

t1 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
elapsed = time.time() - t1

if r.returncode != 0:
    print(f"[ECHEC] code={r.returncode}")
    print(r.stderr[-3000:])
    sys.exit(1)

sz = os.path.getsize(output_path)
print(f"[OK] chunk_{CHUNK_ID}.wav — {sz / 1024:.0f} KB — {elapsed:.1f}s")
