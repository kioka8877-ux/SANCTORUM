import os, json, sys, time, subprocess, wave, struct
import urllib.request, base64

CHUNK_ID    = os.environ["CHUNK_ID"]
PROJECT_ID  = os.environ.get("PROJECT_ID", "")
TOKEN       = os.environ.get("GH_PAT", "")
MODEL_PATH  = os.environ.get("OMNIVOICE_MODEL_PATH", "/tmp/omnivoice_model")
output_path = f"/tmp/chunk_{CHUNK_ID}.wav"

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

ref_audio_path = ""
ref_text       = ""

if TOKEN:
    ref_url = "https://api.github.com/repos/kioka8877-ux/SANCTORUM/contents/SHARED/IN/ref_voice.mp3"
    try:
        req = urllib.request.Request(ref_url, headers={"Authorization": f"token {TOKEN}"})
        with urllib.request.urlopen(req) as r:
            meta = json.load(r)

        if meta.get("content") and meta.get("encoding") == "base64":
            audio_bytes = base64.b64decode(meta["content"])
        elif meta.get("download_url"):
            dl_req = urllib.request.Request(
                meta["download_url"],
                headers={"Authorization": f"token {TOKEN}"}
            )
            with urllib.request.urlopen(dl_req) as r:
                audio_bytes = r.read()
        else:
            raise RuntimeError("Pas de contenu ni de download_url")

        raw_path = "/tmp/ref_voice_raw.mp3"
        with open(raw_path, "wb") as f:
            f.write(audio_bytes)
        print(f"[REF] ref_voice.mp3 telecharge ({len(audio_bytes)//1024} KB)")

        ref_wav = "/tmp/ref_voice.wav"
        conv = subprocess.run(
            ["ffmpeg", "-y", "-f", "mp3", "-i", raw_path,
             "-ar", "24000", "-ac", "1", ref_wav],
            capture_output=True
        )
        if conv.returncode != 0:
            raise RuntimeError("Conversion WAV echouee")

        ref_wav_trim = "/tmp/ref_voice_trim.wav"
        trim = subprocess.run(
            ["ffmpeg", "-y", "-i", ref_wav,
             "-t", "15",
             "-ar", "24000", "-ac", "1", ref_wav_trim],
            capture_output=True
        )
        if trim.returncode == 0:
            ref_audio_path = ref_wav_trim
            print("[REF] Converti + tronque a 15s OK")
        else:
            ref_audio_path = ref_wav
            print("[REF] Converti en WAV OK (trim echoue — fichier complet)")

    except Exception as e:
        print(f"[REF] Erreur: {e} — mode auto_voice")
        ref_audio_path = ""

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

print(f"[MODEL] Utilisation modele depuis {MODEL_PATH}")
if not os.path.exists(MODEL_PATH):
    print(f"[MODEL] ERREUR — modele absent de {MODEL_PATH}")
    sys.exit(1)
print(f"[MODEL] OK")

cmd = [
    "omnivoice-infer",
    "--model", MODEL_PATH,
    "--text", text,
    "--language", "fr",
    "--output", output_path,
]
if ref_audio_path and os.path.exists(ref_audio_path):
    cmd += ["--ref_audio", ref_audio_path]
    print("[MODE] voice_clone")
    if ref_text:
        cmd += ["--ref_text", ref_text]
        print("[MODE] + ref_text fourni")
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
