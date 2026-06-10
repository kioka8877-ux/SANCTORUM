"""
SR_CUSTOS.py — Gardien de la Flotte SANCTORUM
==============================================
Équivalent de CRS_CUSTOS.py dans PENTERACT DORN.
Seul agent autorisé à modifier fleet_status dans liber_sanctorum.json.

Usage:
    python SR_CUSTOS.py --mode check-out  --frigate F01
    python SR_CUSTOS.py --mode check-in   --frigate F01 --output voix_brute.wav
    python SR_CUSTOS.py --mode validate   --schema liber_sanctorum.json
    python SR_CUSTOS.py --mode status
"""

import argparse
import json
import os
import hashlib
from datetime import datetime, timezone

CMS_PATH    = "liber_sanctorum.json"
CAMPAIGN_LOG = "TRACKING/SR_CAMPAIGN_LOG.md"
TRANSFER_LOG = "TRACKING/SR_TRANSFER_LOG.md"

VALID_FRIGATES = ["F01", "F02", "F03A", "F03B"]

FLEET_STATUS_FLOW = [
    "pending_sanctification",
    "voice_raw_ready",
    "voice_purified_ready",
    "directives_ready",
    "music_ready",
    "audio_ready",
    "complete",
]

FRIGATE_STATUS_KEY = {
    "F01":  "f01_dominion",
    "F02":  "f02_celestian",
    "F03A": "f03_seraphim",
    "F03B": "f03_seraphim",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_cms() -> dict:
    with open(CMS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cms(data: dict):
    with open(CMS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def log_campaign(event: str):
    os.makedirs("TRACKING", exist_ok=True)
    ts = now_iso()
    entry = f"\n## [{ts}] {event}\n"
    with open(CAMPAIGN_LOG, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[SR_CUSTOS] LOG: {event}")


def log_transfer(source: str, dest: str, md5: str, status: str):
    os.makedirs("TRACKING", exist_ok=True)
    ts = now_iso()
    entry = f"| {ts} | {source} | {dest} | {md5} | {status} |\n"
    header_needed = not os.path.exists(TRANSFER_LOG)
    with open(TRANSFER_LOG, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("| TIMESTAMP | SOURCE | DEST | MD5 | STATUS |\n")
            f.write("|-----------|--------|------|-----|--------|\n")
        f.write(entry)


def cmd_check_out(frigate: str):
    if frigate not in VALID_FRIGATES:
        print(f"[SR_CUSTOS] ERREUR: Frégate inconnue '{frigate}'")
        return

    cms = load_cms()
    key = FRIGATE_STATUS_KEY[frigate]
    cms[key]["status"] = "processing"
    cms["sr_custos"]["last_validation"] = now_iso()
    save_cms(cms)
    log_campaign(f"{frigate} — check-out — status: processing")
    print(f"[SR_CUSTOS] {frigate} autorisée à lire ses entrées.")


def cmd_check_in(frigate: str, output_path: str):
    if frigate not in VALID_FRIGATES:
        print(f"[SR_CUSTOS] ERREUR: Frégate inconnue '{frigate}'")
        return

    if not os.path.exists(output_path):
        print(f"[SR_CUSTOS] ERREUR: Fichier de sortie introuvable: {output_path}")
        cms = load_cms()
        cms[FRIGATE_STATUS_KEY[frigate]]["status"] = "error"
        cms["sr_custos"]["errors"].append(
            {"ts": now_iso(), "frigate": frigate, "msg": f"Output not found: {output_path}"}
        )
        save_cms(cms)
        return

    file_md5 = md5_file(output_path)
    cms = load_cms()
    key = FRIGATE_STATUS_KEY[frigate]
    cms[key]["status"] = "done"
    cms[key]["output_path"] = output_path
    cms["sr_custos"]["last_validation"] = now_iso()
    cms["sr_custos"]["errors"] = [e for e in cms["sr_custos"]["errors"]
                                   if e.get("frigate") != frigate]

    _advance_fleet_status(cms, frigate)
    save_cms(cms)

    log_transfer(f"{frigate}/CODEBASE", f"{frigate}/OUT/{os.path.basename(output_path)}",
                 file_md5, "OK")
    log_campaign(f"{frigate} — check-in — output: {output_path} — md5: {file_md5} — status: done")
    print(f"[SR_CUSTOS] {frigate} validée. fleet_status: {cms['fleet_status']}")


def _advance_fleet_status(cms: dict, completed_frigate: str):
    transitions = {
        "F01":  "voice_raw_ready",
        "F02":  "voice_purified_ready",
        "F03A": "directives_ready",
        "F03B": "audio_ready",
    }
    if completed_frigate in transitions:
        cms["fleet_status"] = transitions[completed_frigate]


def cmd_validate(schema_path: str):
    required_keys = [
        "fleet_status", "bpm",
        "f01_dominion", "f02_celestian", "f03_seraphim",
        "sr_custos", "final_output"
    ]
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        missing = [k for k in required_keys if k not in data]
        if missing:
            print(f"[SR_CUSTOS] SCHEMA INVALIDE — Clés manquantes: {missing}")
        else:
            print(f"[SR_CUSTOS] SCHEMA VALIDE — {schema_path}")
            log_campaign(f"Schema validation PASS — {schema_path}")
    except json.JSONDecodeError as e:
        print(f"[SR_CUSTOS] ERREUR JSON: {e}")


def cmd_status():
    cms = load_cms()
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║          SR_CUSTOS — ÉTAT DE LA FLOTTE               ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  fleet_status  : {cms['fleet_status']:<36}║")
    print(f"║  bpm           : {str(cms.get('bpm','null')):<36}║")
    print(f"║  F01 DOMINION  : {cms['f01_dominion']['status']:<36}║")
    print(f"║  F02 CELESTIAN : {cms['f02_celestian']['status']:<36}║")
    print(f"║  F03 SERAPHIM  : {cms['f03_seraphim']['status']:<36}║")
    print(f"║  Last validation: {cms['sr_custos']['last_validation'] or 'jamais':<35}║")
    errors = cms['sr_custos']['errors']
    print(f"║  Erreurs       : {str(len(errors)):<36}║")
    print("╚══════════════════════════════════════════════════════╝\n")


def main():
    parser = argparse.ArgumentParser(description="SR_CUSTOS — Gardien de la Flotte SANCTORUM")
    parser.add_argument("--mode", required=True,
                        choices=["check-out", "check-in", "validate", "status"])
    parser.add_argument("--frigate", default=None)
    parser.add_argument("--output",  default=None)
    parser.add_argument("--schema",  default=CMS_PATH)
    args = parser.parse_args()

    if args.mode == "check-out":
        if not args.frigate:
            print("[SR_CUSTOS] --frigate requis pour check-out")
            return
        cmd_check_out(args.frigate)

    elif args.mode == "check-in":
        if not args.frigate or not args.output:
            print("[SR_CUSTOS] --frigate et --output requis pour check-in")
            return
        cmd_check_in(args.frigate, args.output)

    elif args.mode == "validate":
        cmd_validate(args.schema)

    elif args.mode == "status":
        cmd_status()


if __name__ == "__main__":
    main()
