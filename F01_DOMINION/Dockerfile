FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends     ffmpeg git git-lfs     && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir     omnivoice     openai-whisper     pydub     huggingface_hub

# Pre-cache Whisper base model (139MB baked in image — zero download at runtime)
RUN python -c "import whisper; whisper.load_model('base')"

WORKDIR /workspace
