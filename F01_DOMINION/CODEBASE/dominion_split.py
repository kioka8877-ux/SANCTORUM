import os, json, re, sys, base64
import urllib.request

TOKEN = os.environ["GH_PAT"]
PROJECT_ID = os.environ["PROJECT_ID"]
N = int(os.environ.get("N_WORKERS", "10"))


def fetch_script(project_id):
    for path in [
        f"F01_SANGUIS/OUT/script_{project_id}.md",
        "F01_SANGUIS/OUT/script_002.md",
    ]:
        url = f"https://api.github.com/repos/kioka8877-ux/ANGRON-V2/contents/{path}"
        req = urllib.request.Request(url, headers={"Authorization": f"token {TOKEN}"})
        try:
            with urllib.request.urlopen(req) as r:
                d = json.load(r)
                print(f"[SPLIT] Script lu : {path}")
                return base64.b64decode(d["content"]).decode()
        except Exception as e:
            print(f"[SPLIT] {path} introuvable: {e}")
    raise RuntimeError("Aucun script trouve dans ANGRON-V2")


def extract_spoken(md):
    lines = md.splitlines()
    spoken = []
    skip = False

    for line in lines:
        # Stop at metadata/notes sections — not spoken
        if re.match(r"#+.*(METADONN|NOTES LACERAT|NOTES |YOUTUBE)", line, re.IGNORECASE):
            break

        if re.match(r"#+.*HOOK VISUEL", line):
            skip = True
        elif re.match(r"#+", line) and "HOOK VISUEL" not in line:
            skip = False

        if skip:
            continue
        if re.match(r"#+", line):
            continue
        # Filter header metadata fields and stage directions
        if re.match(r"\*\[|\*Le |---|\*\*Format|\*\*Mode|\*\*Langue|\*\*Dur|\*\*Concept|\*\*Hook|\*\*Ton", line):
            continue

        text = re.sub(r"\[ANIM:[^\]]*\]", "", line)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"\[[^\]]*\]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            spoken.append(text)

    return " ".join(spoken)


def split_chunks(text, n):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s for s in sentences if s.strip()]
    n = min(n, len(sentences))
    base, extra = divmod(len(sentences), n)
    chunks = {}
    idx = 0
    for i in range(n):
        size = base + (1 if i < extra else 0)
        chunks[str(i)] = " ".join(sentences[idx: idx + size])
        idx += size
    return chunks


script_md = fetch_script(PROJECT_ID)
spoken = extract_spoken(script_md)
chunks = split_chunks(spoken, N)

print(f"[SPLIT] {len(spoken)} chars => {len(chunks)} chunks")
for k, v in chunks.items():
    print(f"  chunk {k}: {len(v)} chars | {v[:80]}...")

with open("/tmp/chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)
print("[SPLIT] /tmp/chunks.json OK")
