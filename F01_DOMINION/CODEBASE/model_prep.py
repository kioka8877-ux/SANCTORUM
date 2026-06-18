import subprocess, sys, os, shutil

MODEL_DIR = "/tmp/omnivoice_model"

# Remove incomplete dir if exists
if os.path.exists(MODEL_DIR):
    shutil.rmtree(MODEL_DIR)

print("[MODEL-PREP] Cloning k2-fsa/OmniVoice via git+lfs...")
env = os.environ.copy()
env["GIT_LFS_SKIP_SMUDGE"] = "0"

# Install git-lfs first
subprocess.run(["sudo", "apt-get", "install", "-y", "-q", "git-lfs"], check=True)
subprocess.run(["git", "lfs", "install"], check=True)

result = subprocess.run(
    ["git", "clone", "--depth=1", "https://huggingface.co/k2-fsa/OmniVoice", MODEL_DIR],
    env=env,
    timeout=900
)

if result.returncode != 0:
    print("[MODEL-PREP] git clone failed, trying huggingface_hub fallback...")
    import time
    from huggingface_hub import snapshot_download
    for attempt in range(5):
        try:
            snapshot_download(repo_id="k2-fsa/OmniVoice", local_dir=MODEL_DIR)
            print("[MODEL-PREP] snapshot_download OK")
            sys.exit(0)
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            wait = 60 * (attempt + 1)
            print(f"Waiting {wait}s before retry...")
            time.sleep(wait)
    sys.exit(1)

# Verify model files present
files = os.listdir(MODEL_DIR)
print(f"[MODEL-PREP] Model ready — {len(files)} files: {files[:5]}")
sys.exit(0)
