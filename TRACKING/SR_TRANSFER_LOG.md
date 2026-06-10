# SR_TRANSFER_LOG — Journal des Transferts Inter-Frégates

> Log de tous les transferts de fichiers entre frégates.
> Chaque entrée : source, destination, hash MD5, timestamp, statut.
> Géré automatiquement par `SR_CUSTOS.py`. Ne pas modifier manuellement.

---

## Transferts en attente de première exécution

Les transferts inter-frégates seront enregistrés automatiquement par `SR_CUSTOS.py --mode check-in`
lors de l'exécution des notebooks dans l'ordre suivant :

| Ordre | Source | Destination | Fichier attendu | Déclencheur |
|-------|--------|-------------|-----------------|-------------|
| 1 | F01_DOMINION/CODEBASE | F01_DOMINION/OUT/ | voix_brute.wav | SR_CUSTOS --frigate F01 --mode check-in |
| 2 | F01_DOMINION/OUT | F02_CELESTIAN/IN/ | voix_brute.wav | Manuel / auto via liber |
| 3 | F02_CELESTIAN/CODEBASE | F02_CELESTIAN/OUT/ | voix_purifiee.wav | SR_CUSTOS --frigate F02 --mode check-in |
| 4 | F03_SERAPHIM/CODEBASE | F03_SERAPHIM/CODEBASE/ | directives.json | Export F03A (inline liber) |
| 5 | F03_SERAPHIM/CODEBASE | F03_SERAPHIM/OUT/ | master_audio_mix.mp3 | SR_CUSTOS --frigate F03B --mode check-in |
| 6 | F03_SERAPHIM/OUT | SHARED/OUT/ | final_sanctorum.mp3 | F03B export automatique |

---

## Historique des transferts exécutés

| TIMESTAMP | SOURCE | DEST | MD5 | STATUS |
|-----------|--------|------|-----|--------|
| — | — | — | — | En attente de première exécution |

---
