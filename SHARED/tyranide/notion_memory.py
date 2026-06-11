"""
TYRANIDE — NOTION MEMORY
Sync bidirectionnel entre GitHub JSON (source de vérité) et Notion DB (dashboard humain).
Optionnel : fonctionne sans Notion. Sans NOTION_TOKEN, les fonctions sont des no-ops silencieux.

Variables d'environnement requises (Colab Secrets ou GitHub Secrets) :
  NOTION_TOKEN          — Integration token Notion
  NOTION_DB_CICATRICES  — Database ID table cicatrices
  NOTION_DB_VACCINS     — Database ID table vaccins
  NOTION_DB_INCIDENTS   — Database ID table incidents SOS
  NOTION_DB_FLOTTE      — Database ID table flotte
"""

import os, json, urllib.request, urllib.error
from datetime import datetime

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _token():
    return os.environ.get("NOTION_TOKEN", "")


def _headers():
    return {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _post(endpoint, payload):
    if not _token():
        return None
    try:
        req = urllib.request.Request(
            f"{NOTION_API}/{endpoint}",
            data=json.dumps(payload).encode(),
            headers=_headers(),
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [NOTION] Erreur : {e}")
        return None


def _rich_text(content):
    return [{"type": "text", "text": {"content": str(content)[:2000]}}]


def _select(name):
    return {"name": str(name)}


# ── ÉCRITURE ──────────────────────────────────────────────────────────

def write_cicatrice(id_, nom, signature, symptome, cause, fix, compartiment,
                    fregate, statut, fois, commit=None):
    """Ajoute ou met à jour une cicatrice dans Notion."""
    db_id = os.environ.get("NOTION_DB_CICATRICES")
    if not db_id:
        return None
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "ID":            {"title": _rich_text(id_)},
            "Nom":           {"rich_text": _rich_text(nom)},
            "Signature":     {"rich_text": _rich_text(signature)},
            "Symptôme":      {"rich_text": _rich_text(symptome)},
            "Cause_Racine":  {"rich_text": _rich_text(cause)},
            "Fix_Validé":    {"rich_text": _rich_text(fix)},
            "Compartiment":  {"select": _select(compartiment)},
            "Frégate":       {"select": _select(fregate)},
            "Statut":        {"select": _select(statut)},
            "Fois_Rencontré":{"number": int(fois)},
        },
    }
    if commit:
        payload["properties"]["Commit_Fix"] = {"url": f"https://github.com/kioka8877-ux/SANCTORUM/commit/{commit}"}
    return _post("pages", payload)


def write_vaccin(id_, package, version, compatible_avec, fregate, statut):
    db_id = os.environ.get("NOTION_DB_VACCINS")
    if not db_id:
        return None
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Package":          {"title": _rich_text(package)},
            "ID":               {"rich_text": _rich_text(id_)},
            "Version_Validée":  {"rich_text": _rich_text(version)},
            "Compatible_Avec":  {"rich_text": _rich_text(compatible_avec)},
            "Frégate":          {"select": _select(fregate)},
            "Statut":           {"select": _select(statut)},
            "Validé_Le":        {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
        },
    }
    return _post("pages", payload)


def write_incident(fregate, tentatives, logs_erreur, solutions_tentees, question):
    """Crée un incident SOS dans Notion après N échecs."""
    db_id = os.environ.get("NOTION_DB_INCIDENTS")
    if not db_id:
        return None
    id_ = f"INC-{datetime.now().strftime('%Y%m%d-%H%M')}"
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "ID":                {"title": _rich_text(id_)},
            "Frégate":           {"rich_text": _rich_text(fregate)},
            "Tentatives":        {"number": int(tentatives)},
            "Logs_Erreur":       {"rich_text": _rich_text(logs_erreur)},
            "Solutions_Tentées": {"rich_text": _rich_text(solutions_tentees)},
            "Question_Opérateur":{"rich_text": _rich_text(question)},
            "Statut":            {"select": _select("EN ATTENTE")},
        },
    }
    return _post("pages", payload)


def update_flotte(fregate, statut):
    """Met à jour le statut d'une frégate dans la table FLOTTE."""
    db_id = os.environ.get("NOTION_DB_FLOTTE")
    if not db_id:
        return None
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Frégate": {"title": _rich_text(fregate)},
            "Statut":  {"select": _select(statut)},
            "Dernier_Run": {"date": {"start": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}},
        },
    }
    return _post("pages", payload)


# ── SYNC BULK depuis cicatrices.json ─────────────────────────────────

def sync_all_to_notion(cicatrices_path="cicatrices.json", vaccins_path="vaccins.json"):
    """Charge les JSON locaux et les pousse en masse vers Notion."""
    if not _token():
        print("[NOTION] Pas de token — sync ignorée")
        return

    try:
        with open(cicatrices_path) as f:
            cic_data = json.load(f)
        for c in cic_data["cicatrices"]:
            write_cicatrice(
                c["id"], c["nom"], c["signature"], c["symptome"],
                c["cause_racine"], c["fix_valide"], c["compartiment"],
                c["fregate"], c["statut"], c["fois_rencontree"],
                c.get("commit_fix"),
            )
            print(f"  [NOTION] Cicatrice {c['id']} → OK")
    except Exception as e:
        print(f"  [NOTION] Erreur sync cicatrices : {e}")

    try:
        with open(vaccins_path) as f:
            vac_data = json.load(f)
        for v in vac_data["vaccins"]:
            write_vaccin(
                v["id"], v["package"], v["version"],
                v.get("note", ""), v["fregate"], v["statut"],
            )
            print(f"  [NOTION] Vaccin {v['id']} ({v['package']}) → OK")
    except Exception as e:
        print(f"  [NOTION] Erreur sync vaccins : {e}")


# ── CLI pour GitHub Actions ───────────────────────────────────────────

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if "--report-incident" in args:
        fregate = args[args.index("--fregate") + 1] if "--fregate" in args else "INCONNU"
        logs    = args[args.index("--logs") + 1]    if "--logs"    in args else "no logs"
        result  = write_incident(
            fregate=fregate,
            tentatives=1,
            logs_erreur=logs,
            solutions_tentees="CI GitHub Actions — premier échec",
            question="Le pipeline CI a échoué. Voir les logs GitHub Actions attachés.",
        )
        print(f"[NOTION] Incident créé : {result.get('id') if result else 'token absent'}")
    elif "--sync" in args:
        sync_all_to_notion()
