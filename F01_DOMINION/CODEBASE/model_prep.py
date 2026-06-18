import time, sys
from huggingface_hub import snapshot_download

for attempt in range(3):
    try:
        snapshot_download(repo_id="k2-fsa/OmniVoice", local_dir="/tmp/omnivoice_model")
        print("Model downloaded OK")
        sys.exit(0)
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")
        if attempt < 2:
            time.sleep(30)
        else:
            sys.exit(1)
