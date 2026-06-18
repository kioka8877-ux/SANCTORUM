import os, json, sys, time, subprocess, wave, struct, tempfile
import urllib.request, base64
from huggingface_hub import snapshot_download

CHUNK_ID    = os.environ["CHUNK_ID"]
PROJECT_ID  = os.environ.get("PROJECT_ID", "")
TOKEN       = os.environ.get("GH_PAT", "")
output_path = f"/tmp/chunk_{CHUNK_ID}.wav"

# ── Lecture du chunk ──────────────────────────────────────────────────────
with open("/tmp/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

text = chunks.get(str(CHUNK_ID), "").strip()

if not text:
    print(f"[WORKER {CHUNK_ID}] Chunk vide — silence")
    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(22050)
        wf.writeframes(struct.pack("<h", 0) * 2205)
    sys.exit(0)

print(f"[WORKER {CHUNK_ID}] {len(text)} chars : {text[:80]}...")

# ── Telechargement voix reference depuis SANCTORUM ────────────────────────
ref_audio_path = ""
ref_text       = ""

if TOKEN:
    ref_url = "https://api.github.com/repos/kioka8877-ux/SANCTORUM/contents/SHARED/IN/ref_voice.mp3"
    try:
        req = urllib.request.Request(ref_url, headers={"Authorization": f"token {TOKEN}"})
        with urllib.request.urlopen(req) as r:
            data = json.load(r)
        audio_bytes = base64.b64decode(data["content"])
        ref_audio_path = "/tmp/ref_voice.mp3"
        with open(ref_audio_path, "wb") as f:
            f.write(audio_bytes)
        print(f"[REF] ref_voice.mp3 telecharge ({len(audio_bytes)//1024} KB)")
    except Exception as e:
        print(f"[REF] Introuvable ou erreur: {e} — mode auto_voice")
        ref_audio_path = ""

# ── Auto-transcription de la voix reference (si disponible) ──────────────
if ref_audio_path:
    try:
        import whisper
        wmodel = whisper.load_model("base")
        result = wmodel.transcribe(ref_audio_path, language="fr")
        ref_text = result["text"].strip()
        print(f"[WHISPER] ref_text : {ref_text[:100]}...")
    except Exception as e:
        print(f"[WHISPER] Erreur transcription: {e} — ref_text vide")
        ref_text = ""

# ── Telechargement modele OmniVoice ──────────────────────────────────────
t0 = time.time()
snapshot_download(repo_id="k2-fsa/OmniVoice", local_dir="/tmp/omnivoice_model")
print(f"[MODEL] {time.time() - t0:.1f}s — pret")

# ── Inference OmniVoice ───────────────────────────────────────────────────
cmd = [
    "omnivoice-infer",
    "--model", "/tmp/omnivoice_model",
    "--text", text,
    "--language", "fr",
    "--output", output_path,
]
if ref_audio_path and os.path.exists(ref_audio_path):
    cmd += ["--ref_audio", ref_audio_path]
    print("[MODE] voice_clone")
    if ref_text:
        cmd += ["--ref_text", ref_text]
        print(f"[MODE] + ref_text fourni")
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
print(f"[OK] chunk_{CHUNK_ID}.wav — {sz/1024:.0f} KB — {elapsed:.1f}s")
