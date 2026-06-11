"""
TYRANIDE — VACCIN LOADER
Lit vaccins.json depuis GitHub, construit et applique les commandes pip.
Utilisé par la cellule C0 du notebook.
"""

import subprocess, sys, json
from urllib.request import urlopen
from urllib.error import URLError

VACCINS_URL = (
    "https://raw.githubusercontent.com/kioka8877-ux/SANCTORUM/main/"
    "SHARED/tyranide/vaccins.json"
)
CICATRICES_URL = (
    "https://raw.githubusercontent.com/kioka8877-ux/SANCTORUM/main/"
    "SHARED/tyranide/cicatrices.json"
)


def charger_vaccins(fregate=None, compartiment=None, inclure_conflits=False):
    """
    Lit vaccins.json depuis GitHub.
    Retourne une liste de dicts vaccin filtrée selon fregate/compartiment.
    """
    try:
        with urlopen(VACCINS_URL, timeout=10) as r:
            data = json.loads(r.read())
        vaccins = data.get("vaccins", [])
    except URLError as e:
        print(f"  [TYRANIDE] Mémoire hors ligne : {e}")
        return []

    result = []
    for v in vaccins:
        if fregate and v.get("fregate") != fregate:
            continue
        if compartiment and v.get("compartiment") != compartiment:
            continue
        if v["statut"] == "VALIDÉ":
            result.append(v)
        elif v["statut"] == "CONFLIT_OUVERT" and inclure_conflits:
            result.append(v)
    return result


def appliquer_vaccins(vaccins, verbose=True):
    """
    Lance pip install pour chaque vaccin validé.
    Retourne (succes, echecs).
    """
    succes, echecs = [], []
    for v in vaccins:
        pkg = v["package"]
        ver = v["version"]
        extra = v.get("extra_index")
        cmd = [sys.executable, "-m", "pip", "install", "-q", f"{pkg}=={ver}"]
        if extra:
            cmd += ["--extra-index-url", extra]
        if verbose:
            print(f"  [VAC] {pkg}=={ver} ...", end=" ")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            succes.append(pkg)
            if verbose:
                print("OK")
        else:
            echecs.append({"package": pkg, "erreur": r.stderr[-200:]})
            if verbose:
                print(f"FAIL : {r.stderr[-100:]}")
    return succes, echecs


def afficher_cicatrices_ouvertes():
    """Affiche les cicatrices non résolues pour information."""
    try:
        with urlopen(CICATRICES_URL, timeout=10) as r:
            data = json.loads(r.read())
        ouvertes = [c for c in data.get("cicatrices", []) if c["statut"] != "RÉSOLU"]
        if ouvertes:
            print(f"\n  [TYRANIDE] {len(ouvertes)} cicatrice(s) OUVERTES :")
            for c in ouvertes:
                print(f"    ⚠  {c['id']} — {c['nom']}")
    except Exception:
        pass


def vaccination_complete(fregate="F01_DOMINION", verbose=True):
    """
    Point d'entrée principal pour la cellule C0.
    Lit, filtre, applique, rapporte.
    """
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  TYRANIDE — VACCINATION PRÉVENTIVE                       ║")
    print(f"║  Frégate : {fregate:<47}║")
    print("╚══════════════════════════════════════════════════════════╝")

    vaccins = charger_vaccins(fregate=fregate)
    if not vaccins:
        print("  [TYRANIDE] Aucun vaccin trouvé — C2 tournera sans vaccination")
        return False

    print(f"  [TYRANIDE] {len(vaccins)} vaccin(s) chargé(s) depuis GitHub")
    succes, echecs = appliquer_vaccins(vaccins, verbose=verbose)

    print(f"\n  [OK] {len(succes)} vaccin(s) appliqué(s)")
    if echecs:
        print(f"  [!!] {len(echecs)} échec(s) : {[e['package'] for e in echecs]}")

    afficher_cicatrices_ouvertes()
    print("\n  [TYRANIDE] Immunisation terminée — C2 peut démarrer\n")
    return len(echecs) == 0
