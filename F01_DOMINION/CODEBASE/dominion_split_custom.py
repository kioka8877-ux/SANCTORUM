import os, json, re, sys

N = int(os.environ.get("N_WORKERS", "10"))
SCRIPT_PATH = os.environ.get("CUSTOM_SCRIPT_PATH", "F01_DOMINION/IN/custom_script.md")

with open(SCRIPT_PATH, encoding="utf-8") as f:
    md = f.read()

print(f"[SPLIT] Script lu : {SCRIPT_PATH} ({len(md)} chars)")

lines = md.splitlines()
spoken = []

for line in lines:
    text = line.strip()
    if not text:
        continue
    # Remove section markers like [ACCROCHE], [BRAND 1: ...]
    text = re.sub(r"^\[[^\]]+\]\s*", "", text)
    # Remove emphasis brackets [word] -> word
    text = re.sub(r"\[([^\]]+)\]", r"\1", text)
    # Clean markdown
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text:
        spoken.append(text)

full_text = " ".join(spoken)
print(f"[SPLIT] Texte parle extrait : {len(full_text)} chars")

sentences = re.split(r"(?<=[.!?])\s+", full_text.strip())
sentences = [s for s in sentences if s.strip()]
print(f"[SPLIT] {len(sentences)} phrases detectees")

n = min(N, len(sentences))
base, extra = divmod(len(sentences), n)
chunks = {}
idx = 0
for i in range(n):
    size = base + (1 if i < extra else 0)
    chunks[str(i)] = " ".join(sentences[idx: idx + size])
    idx += size

print(f"[SPLIT] {len(chunks)} chunks crees :")
for k, v in chunks.items():
    print(f"  chunk {k}: {len(v):4d} chars | {v[:80]}...")

with open("/tmp/chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)
print("[SPLIT] /tmp/chunks.json OK")
