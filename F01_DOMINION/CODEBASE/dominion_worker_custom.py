import os, json, sys, time, subprocess, wave, struct

CHUNK_ID    = os.environ["CHUNK_ID"]
MODEL_PATH  = os.environ.get("OMNIVOICE_MODEL_PATH", "/tmp/omnivoice_model")
LANGUAGE    = os.environ.get("TTS_LANGUAGE", "en")
output_path = f"/tmp/chunk_{CHUNK_ID}.wav"

with open("/tmp/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

text = chunks.get(str(CHUNK_ID), "").strip()

if not text:
    print(f"[WORKER {CHUNK_ID}] Chunk vide - silence")
    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(22050)
        wf.writeframes(struct.pack("<h", 0) * 2205)
    sys.exit(0)

print(f"[WORKER {CHUNK_ID}] {len(text)} chars : {text[:80]}...")

ref_text = ""
ref_audio_path = "/tmp/ref_voice_trim.wav"

if os.path.exists("/tmp/ref_text.txt"):
    with open("/tmp/ref_text.txt", encoding="utf-8") as f:
        ref_text = f.read().strip()
    print(f"[REF] ref_text loaded ({len(ref_text)} chars)")

if not os.path.exists(ref_audio_path) or os.path.getsize(ref_audio_path) == 0:
    ref_audio_path = ""
    print("[REF] ref_voice_trim.wav absent ou vide - auto_voice")

print(f"[MODEL] Using model from {MODEL_PATH}")
if not os.path.exists(MODEL_PATH):
    print(f"[MODEL] ERROR - model missing from {MODEL_PATH}")
    sys.exit(1)
print(f"[MODEL] OK")

cmd = [
    "omnivoice-infer",
    "--model", MODEL_PATH,
    "--text", text,
    "--language", LANGUAGE,
    "--output", output_path,
]
if ref_audio_path:
    cmd += ["--ref_audio", ref_audio_path]
    print("[MODE] voice_clone")
    if ref_text:
        cmd += ["--ref_text", ref_text]
        print("[MODE] + ref_text fourni")
else:
    print("[MODE] auto_voice")

t1 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
elapsed = time.time() - t1

if r.returncode != 0:
    print(f"[FAILED] code={r.returncode}")
    print(r.stderr[-3000:])
    sys.exit(1)

sz = os.path.getsize(output_path)
print(f"[OK] chunk_{CHUNK_ID}.wav - {sz/1024:.0f} KB - {elapsed:.1f}s")
