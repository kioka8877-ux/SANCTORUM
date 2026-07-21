import subprocess, sys, os, shutil, json
import urllib.request, base64

MODEL_DIR = "/tmp/omnivoice_model"
TOKEN = os.environ.get("GH_PAT", "")

if os.path.exists(MODEL_DIR):
    shutil.rmtree(MODEL_DIR)

print("[MODEL-PREP] Cloning k2-fsa/OmniVoice via git+lfs...")
env = os.environ.copy()
env["GIT_LFS_SKIP_SMUDGE"] = "0"
subprocess.run(["git", "lfs", "install"], check=True)

result = subprocess.run(
    ["git", "clone", "--depth=1", "https://huggingface.co/k2-fsa/OmniVoice", MODEL_DIR],
    env=env, timeout=900
)

if result.returncode != 0:
    print("[MODEL-PREP] git clone failed, fallback huggingface_hub...")
    import time
    from huggingface_hub import snapshot_download
    for attempt in range(5):
        try:
            snapshot_download(repo_id="k2-fsa/OmniVoice", local_dir=MODEL_DIR)
            print("[MODEL-PREP] snapshot_download OK")
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(60 * (attempt + 1))
    else:
        sys.exit(1)

files = os.listdir(MODEL_DIR)
print(f"[MODEL-PREP] Model ready — {len(files)} files: {files[:5]}")

# --- OPTION B: Whisper une seule fois ici ---
# --- OPTION C: Trim 5s au lieu de 15s ---
ref_text = ""
ref_wav_trim = "/tmp/ref_voice_trim.wav"

if TOKEN:
    try:
        ref_url = "https://api.github.com/repos/kioka8877-ux/SANCTORUM/contents/SHARED/IN/ref_voice.mp3"
        req = urllib.request.Request(ref_url, headers={"Authorization": f"token {TOKEN}"})
        with urllib.request.urlopen(req) as r:
            meta = json.load(r)

        if meta.get("content") and meta.get("encoding") == "base64":
            audio_bytes = base64.b64decode(meta["content"])
        elif meta.get("download_url"):
            dl_req = urllib.request.Request(meta["download_url"], headers={"Authorization": f"token {TOKEN}"})
            with urllib.request.urlopen(dl_req) as r:
                audio_bytes = r.read()
        else:
            raise RuntimeError("No content or download_url")

        raw_path = "/tmp/ref_voice_raw.mp3"
        with open(raw_path, "wb") as f:
            f.write(audio_bytes)
        print(f"[REF] Downloaded ref_voice.mp3 ({len(audio_bytes)//1024} KB)")

        ref_wav = "/tmp/ref_voice.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "mp3", "-i", raw_path, "-ar", "24000", "-ac", "1", ref_wav],
            capture_output=True, check=True
        )
        # Trim duration configurable via TRIM_SECONDS env var (default 20)
        trim_sec = os.environ.get("TRIM_SECONDS", "20")
        subprocess.run(
            ["ffmpeg", "-y", "-i", ref_wav, "-t", trim_sec, "-ar", "24000", "-ac", "1", ref_wav_trim],
            capture_output=True, check=True
        )
        print(f"[REF] Converted + trimmed to {trim_sec}s OK")

        import whisper
        wmodel = whisper.load_model("base")
        result_w = wmodel.transcribe(ref_wav_trim, language="fr")
        ref_text = result_w["text"].strip()
        print(f"[WHISPER] ref_text (1x run): {ref_text[:100]}...")

    except Exception as e:
        print(f"[WHISPER/REF] Error: {e} — workers will use auto_voice")
        ref_wav_trim = ""
        ref_text = ""

# Sauvegarder pour les workers (via artifact)
with open("/tmp/ref_text.txt", "w", encoding="utf-8") as f:
    f.write(ref_text)
print(f"[MODEL-PREP] ref_text.txt saved ({len(ref_text)} chars)")

if not os.path.exists(ref_wav_trim):
    open("/tmp/ref_voice_trim.wav", "wb").close()
    print("[MODEL-PREP] ref_voice_trim.wav vide (fallback auto_voice)")

sys.exit(0)
