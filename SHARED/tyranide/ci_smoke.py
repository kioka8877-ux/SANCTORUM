"""
TYRANIDE — CI SMOKE TEST (CPU)
Exécuté par GitHub Actions — vérifie que le projet ne casse pas sur CPU.
Ne teste PAS les features GPU (torch CUDA, F5TTS inference) — juste les imports et configs.
"""

import sys, json, subprocess, os

VACCINS_PATH = os.path.join(os.path.dirname(__file__), "vaccins.json")
CICATRICES_PATH = os.path.join(os.path.dirname(__file__), "cicatrices.json")
ERROR_LOG = "/tmp/smoke_error.txt"

RAPPORT = []


def _ok(msg):
    RAPPORT.append(f"[OK] {msg}")
    print(f"  [OK] {msg}")


def _err(msg):
    RAPPORT.append(f"[!!] {msg}")
    print(f"  [!!] {msg}")
    with open(ERROR_LOG, "a") as f:
        f.write(msg + "\n")


# ── LISTE VACCINS ─────────────────────────────────────────────────────
if "--list-vaccins" in sys.argv:
    with open(VACCINS_PATH) as f:
        data = json.load(f)
    for v in data["vaccins"]:
        if v["statut"] == "VALIDÉ":
            print(f"{v['package']}=={v['version']}")
    sys.exit(0)


# ── INSTALL VACCINS (CPU — sans CUDA) ────────────────────────────────
if "--install-vaccins" in sys.argv:
    with open(VACCINS_PATH) as f:
        data = json.load(f)
    for v in data["vaccins"]:
        if v["statut"] != "VALIDÉ":
            continue
        pkg = v["package"]
        ver = v["version"]
        # Sur CPU CI, on installe torch sans CUDA
        if "cu121" in ver:
            ver_cpu = ver.split("+")[0]
            cmd = [sys.executable, "-m", "pip", "install", "-q", f"{pkg}=={ver_cpu}"]
        else:
            cmd = [sys.executable, "-m", "pip", "install", "-q", f"{pkg}=={ver}"]
        print(f"  [CI] install {pkg}=={ver}...")
        subprocess.run(cmd, capture_output=True)
    sys.exit(0)


# ── SMOKE TEST ────────────────────────────────────────────────────────
if "--smoke-test" in sys.argv:
    open(ERROR_LOG, "w").close()
    print("\n── TYRANIDE CI SMOKE TEST ──────────────────────────────────")

    # Test 1 — imports Python de base
    try:
        import soundfile, librosa, numpy
        _ok(f"soundfile {soundfile.__version__} | librosa {librosa.__version__} | numpy {numpy.__version__}")
    except ImportError as e:
        _err(f"import de base FAIL : {e}")

    # Test 2 — torch importable (CPU)
    try:
        import torch
        _ok(f"torch {torch.__version__} importé")
    except ImportError as e:
        _err(f"torch import FAIL : {e}")

    # Test 3 — transformers pipeline importable
    try:
        from transformers import pipeline as _tp
        _ok("transformers.pipeline importable")
    except Exception as e:
        _err(f"transformers.pipeline FAIL : {e}")

    # Test 4 — gradio importable
    try:
        import gradio as gr
        from gradio.http_server import App
        _ok(f"gradio {gr.__version__} importable")
    except Exception as e:
        _err(f"gradio FAIL : {e}")

    # Test 5 — cicatrices ouvertes
    with open(CICATRICES_PATH) as f:
        cic_data = json.load(f)
    ouvertes = [c for c in cic_data["cicatrices"] if c["statut"] == "OUVERT"]
    if ouvertes:
        for c in ouvertes:
            _err(f"CICATRICE OUVERTE : {c['id']} — {c['nom']}")
    else:
        _ok("Aucune cicatrice ouverte")

    # Test 6 — liber_sanctorum.json lisible
    liber_path = os.path.join(os.path.dirname(__file__), "../../liber_sanctorum.json")
    try:
        with open(liber_path) as f:
            liber = json.load(f)
        _ok(f"liber_sanctorum.json OK — {len(liber)} clé(s)")
    except Exception as e:
        _err(f"liber_sanctorum.json FAIL : {e}")

    # Rapport
    echecs = [l for l in RAPPORT if l.startswith("[!!]")]
    print(f"\n── RÉSULTAT : {'VERT' if not echecs else 'ROUGE'} — {len(RAPPORT) - len(echecs)} OK / {len(echecs)} FAIL")
    sys.exit(1 if echecs else 0)
