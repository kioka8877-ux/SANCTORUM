import time, subprocess, os, psutil, sys
from huggingface_hub import snapshot_download

print("[MODEL] Telechargement k2-fsa/OmniVoice...")
t0 = time.time()
snapshot_download(repo_id="k2-fsa/OmniVoice", local_dir="/tmp/omnivoice_model")
size = subprocess.check_output(["du","-sh","/tmp/omnivoice_model"]).decode().split()[0]
print(f"[MODEL] {time.time()-t0:.0f}s — {size}")

text = "La force de Magnus reside dans la comprehension des lois qui gouvernent l univers. Chaque equation est une verite eternelle."
ram_before = psutil.virtual_memory().available / 1024**3
print(f"[INFER] RAM avant : {ram_before:.1f} GB")

t1 = time.time()
r = subprocess.run(
    ["omnivoice-infer","--model","/tmp/omnivoice_model","--text",text,"--output","/tmp/test_output.wav"],
    capture_output=True, text=True, timeout=600
)
elapsed = time.time() - t1

if r.returncode != 0:
    print(f"[ECHEC] code={r.returncode}")
    print(r.stderr[-3000:])
    sys.exit(1)

sz = os.path.getsize("/tmp/test_output.wav")
ram_after = psutil.virtual_memory().available / 1024**3
audio_dur = sz / (2 * 22050)
print(f"[OK] Temps   : {elapsed:.1f}s")
print(f"[OK] WAV     : {sz/1024:.0f} KB")
print(f"[OK] RAM     : {ram_before-ram_after:.1f} GB consommee")
print(f"[OK] Audio   : {audio_dur:.1f}s")
print(f"[OK] RTF     : {elapsed/max(audio_dur,0.1):.2f}x temps reel")
