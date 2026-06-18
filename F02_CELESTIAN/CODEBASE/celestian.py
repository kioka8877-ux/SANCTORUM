import os, sys, json, base64, urllib.request, tempfile, numpy as np, soundfile as sf
from pedalboard import Pedalboard, HighpassFilter, Compressor, Reverb, NoiseGate
from pydub import AudioSegment
import pyloudnorm as pyln

TOKEN    = os.environ["GH_PAT"]
PROJECT  = os.environ.get("PROJECT_ID", "004")
ANGRON   = "kioka8877-ux/ANGRON-V2"
IN_PATH  = f"F02_LACERAT/IN/voice_{PROJECT}.mp3"

def gh_get(repo, path):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/contents/{path}",
        headers={"Authorization": f"token {TOKEN}"}
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def gh_put(repo, path, content_bytes, sha, message):
    payload = json.dumps({
        "message": message,
        "content": base64.b64encode(content_bytes).decode(),
        "sha": sha
    }).encode()
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/contents/{path}",
        data=payload, method="PUT",
        headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)

# ── 1. Download voice from ANGRON-V2 ────────────────────────────────────
print(f"[CELESTIAN] Fetching {IN_PATH} from ANGRON-V2...")
meta = gh_get(ANGRON, IN_PATH)
raw_mp3 = base64.b64decode(meta["content"].replace("\n",""))
sha = meta["sha"]

tmp_in  = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
tmp_out = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
tmp_in.write(raw_mp3); tmp_in.close()

# ── 2. Convert MP3 → WAV for processing ─────────────────────────────────
seg = AudioSegment.from_mp3(tmp_in.name)
seg = seg.set_channels(1).set_frame_rate(44100)
seg.export(tmp_wav.name, format="wav")
print(f"[CELESTIAN] Audio: {len(seg)/1000:.1f}s mono 44100Hz")

# ── 3. Load as numpy float32 ─────────────────────────────────────────────
samples, sr = sf.read(tmp_wav.name, dtype="float32")
if samples.ndim == 1:
    samples = samples.reshape(1, -1)
else:
    samples = samples.T

# ── 4. DSP chain ─────────────────────────────────────────────────────────
board = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=80.0),          # remove low rumble
    NoiseGate(threshold_db=-38.0, ratio=8.0,            # kill background noise
              attack_ms=5.0, release_ms=150.0),
    Compressor(threshold_db=-15.0, ratio=3.5,           # dynamic control
               attack_ms=5.0, release_ms=100.0),
    Reverb(room_size=0.15, wet_level=0.06,              # subtle presence
           dry_level=0.94, damping=0.6),
])
processed = board(samples, sr)
print("[CELESTIAN] DSP chain applied")

# ── 5. LUFS normalization to -16 LUFS (YouTube standard) ─────────────────
meter = pyln.Meter(sr)
mono  = processed[0] if processed.ndim == 2 else processed
lufs  = meter.integrated_loudness(mono)
print(f"[CELESTIAN] LUFS avant: {lufs:.1f}")
if lufs < -50:
    print("[CELESTIAN] LUFS trop bas — signal silencieux, normalisation ignorée")
else:
    gain  = pyln.normalize.loudness(mono, lufs, -16.0)
    processed = processed * (gain / mono.max() * mono.max()) if mono.max() != 0 else processed
    # simple gain adjustment
    target_lufs = -16.0
    gain_db = target_lufs - lufs
    gain_linear = 10 ** (gain_db / 20.0)
    processed = np.clip(processed * gain_linear, -1.0, 1.0)
    print(f"[CELESTIAN] Gain applique: {gain_db:.1f} dB → -16 LUFS")

# ── 6. Export to MP3 ─────────────────────────────────────────────────────
out_samples = (processed[0] * 32767).astype(np.int16)
out_seg = AudioSegment(
    out_samples.tobytes(), frame_rate=sr,
    sample_width=2, channels=1
)
out_seg.export(tmp_out.name, format="mp3", bitrate="192k")
with open(tmp_out.name, "rb") as f:
    purified_bytes = f.read()
print(f"[CELESTIAN] Export OK — {len(purified_bytes)//1024} KB")

# ── 7. Push purified voice back to ANGRON-V2 ────────────────────────────
res = gh_put(ANGRON, IN_PATH, purified_bytes, sha,
             f"[CELESTIAN] voice_{PROJECT}.mp3 — purifiee DSP -16LUFS")
print(f"[CELESTIAN] Commit: {res['commit']['sha'][:8]}")
print("[CELESTIAN] DONE")
