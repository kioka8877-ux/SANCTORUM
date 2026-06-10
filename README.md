# SANCTORUM — Pipeline Audio Automatisé
> *"Seek perfection of sound, voice, and rhythm."*
> — Ordre de la Rose Sacrée, Adepta Sororitas

```
[░░░░░░░░░░░░░░░░] STRUCTURE ARCHITECTURALE VALIDÉE — FLOTTE AUDIO INITIALISÉE
Phase active    : FORGE DU CODEBASE AUDIO COHÉRENT
Cible           : Google Colab Headless (GPU/CPU) & Google Drive
Coût            : 0.00 EUR
Lien écosystème : PENTERACT DORN (pipeline visuel)
```

---

## Présentation

SANCTORUM est un écosystème d'automatisation et de purification acoustique conçu pour fonctionner de manière autonome sur Google Colab. Il est l'équivalent audio du pipeline visuel [PENTERACT DORN](https://github.com/kioka8877-ux/DORN).

L'objectif central : transformer des voix off brutes et des musiques de trends en **masterpieces acoustiques calibrées au millième de seconde près**, prêtes à être injectées sur les toiles visuelles (Shorts / TikTok / Long-form).

L'esthétique, la nomenclature et la philosophie sont celles des **Sœurs de Bataille — Adepta Sororitas** (Warhammer 40K) : pureté absolue, rigueur disciplinaire, dévotion sans faille.

---

## Architecture — Les Frégates

| Frégate | Nom de Code | Analogie | Rôle |
|---------|-------------|----------|------|
| F01 | DOMINION | Le Prophète | Clonage & Synthèse vocale via OmniVoice |
| F02 | CELESTIAN | La Montre | Purification DSP + Presets personnages |
| F03A | SERAPHIM-A | L'Architecte | Interface visuelle → production JSON directives |
| F03B | SERAPHIM-B | La Machine à Micro-jets | Découpe chirurgicale selon JSON |
| HUD | SANCTORUM-HUD | La Tour de Commandement | Interface centrale de contrôle |

**Principe d'étanchéité :** chaque frégate opère dans son silo `IN/ → CODEBASE/ → OUT/`. La seule communication inter-frégates passe par `liber_sanctorum.json` via `SR_CUSTOS.py`.

---

## Structure du Dépôt

```
SANCTORUM/
├── README.md
├── SR_CUSTOS.py                        ← Gardien de la flotte
├── liber_sanctorum.json                ← CMS centralisé
│
├── TRACKING/
│   ├── SR_CAMPAIGN_LOG.md              ← Log général de campagne
│   └── SR_TRANSFER_LOG.md              ← Log des transferts inter-frégates
│
├── F01_DOMINION/
│   ├── IN/                             ← reference_vocale.wav, script_text.txt
│   ├── OUT/                            ← voix_brute.wav
│   ├── TRACKING/
│   │   └── F01_LOG.md
│   └── CODEBASE/
│       ├── dominion_prophet.ipynb
│       └── requirements_f01.txt
│
├── F02_CELESTIAN/
│   ├── IN/                             ← voix_brute.wav
│   ├── OUT/                            ← voix_purifiee.wav
│   ├── TRACKING/
│   │   └── F02_LOG.md
│   └── CODEBASE/
│       ├── celestian_watch.ipynb
│       ├── requirements_f02.txt
│       └── presets/
│           ├── voix_de_dieu.py
│           ├── echo_chamber.py
│           ├── micro_aeroport.py
│           └── standard_voix_purifiee.py
│
├── F03_SERAPHIM/
│   ├── IN/                             ← trend_music.mp3
│   ├── OUT/                            ← master_audio_mix.mp3
│   ├── TRACKING/
│   │   └── F03_LOG.md
│   └── CODEBASE/
│       ├── seraphim_a_architect.ipynb
│       ├── seraphim_b_microjets.ipynb
│       ├── directives_template.json
│       └── requirements_f03.txt
│
└── SHARED/
    ├── IN/
    └── OUT/                            ← final_sanctorum.mp3
```

---

## Axiomes Impériaux

| # | Axiome | Loi |
|---|--------|-----|
| I | Coût Zéro | 0.00 EUR — stack 100% open-source |
| II | Colab-First | La machine locale est une télécommande |
| III | Isolation Absolue | Zéro appel direct entre frégates |
| IV | Précision Temporelle | Calage en millisecondes, BPM auto, 60fps-ready |
| V | Modularité Presets | Un `.py` dans `presets/` = un nouveau personnage |
| VI | Fork Souverain | OmniVoice forké, jamais modifié |
| VII | Interface Déportée | Gradio headless — navigateur = seul terminal |

---

## Stack Technologique

| Composant | Bibliothèque | Frégate |
|-----------|-------------|---------|
| Synthèse vocale | OmniVoice-Studio (fork) | F01 |
| Interface opérateur | Gradio gr.Blocks | F01, F02, F03A, F03B |
| Communication OmniVoice | httpx | F01 |
| Rack d'effets DSP | Spotify Pedalboard | F02 |
| Presets dynamiques | Python importlib | F02 |
| Détection BPM + aimantation | Librosa | F03A |
| Découpe / assemblage audio | Pydub 0.25+ | F03B |
| Speed/slow sans déformation pitch | pyrubberband | F03B |
| Manipulation échantillons | NumPy | F02, F03B |
| I/O audio haute qualité | soundfile | F03B |
| Stockage | Google Drive | Toutes |
| Calcul | Google Colab | Toutes |

---

## Déploiement Rapide

Chaque frégate possède son propre notebook `.ipynb` dans son répertoire `CODEBASE/`. Pour lancer une frégate :

1. Ouvrir le notebook sur Google Colab
2. Monter Google Drive (cellule 1)
3. Exécuter toutes les cellules
4. Accéder à l'URL Gradio générée dans le navigateur

---

## Lien avec PENTERACT DORN

SANCTORUM est conçu pour s'amarrer à [PENTERACT DORN](https://github.com/kioka8877-ux/DORN). Le `master_audio_mix.mp3` produit par SERAPHIM-B est prêt à être injecté dans le pipeline vidéo DORN en respectant le standard 60fps et la synchronisation au millième de seconde.

---

*Ordre de la Rose Sacrée — Flotte SANCTORUM*
*Que la purification sonore commence.*
