# F03_SERAPHIM — TRACKING LOG

**Nom de code :** SERAPHIM (F03A + F03B)
**Analogies :** F03A = L'Architecte / F03B = La Machine à Micro-jets
**Rôle :** F03A produit le JSON directives · F03B exécute la découpe chirurgicale

---

## Format d'entrée

### F03A — Session Architecte
```
## [TIMESTAMP] F03A Session #N
- Chanson source: fichier.mp3
- BPM détecté: X bpm
- Segments définis: N (queue: 1, loops: N-2, tête: 1)
- Output: directives.json
- SR_CUSTOS validation: PASS / FAIL
```

### F03B — Session Machine à Micro-jets
```
## [TIMESTAMP] F03B Session #N
- directives.json: chemin
- Chanson source: fichier.mp3
- Segments traités: N
- Durée totale assemblée: Xs
- Output: master_audio_mix.mp3
- SR_CUSTOS validation: PASS / FAIL
```

---

## Valeurs par Défaut Actives

| Paramètre | Valeur |
|-----------|--------|
| Volume QUEUE | 100% |
| Volume LOOP | 80% |
| Volume TÊTE | 110% |
| Crossfade transitions | 15ms |
| Fade in TÊTE | 0ms (attaque franche) |
| Fade out TÊTE | 300ms |
| Aimantation beats | Activée |

---

## Sessions

*(Aucune session enregistrée — en attente de première exécution)*

---
