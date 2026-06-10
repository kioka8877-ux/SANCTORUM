# SR_CAMPAIGN_LOG — Journal de Campagne SANCTORUM

> Log chronologique de toutes les activations de frégates, validations, erreurs et événements majeurs.
> Géré automatiquement par `SR_CUSTOS.py`. Ne pas modifier manuellement.
> Exception : les entrées `[CONSTRUCTION]` sont des entrées manuelles documentant la phase de création du projet.

---

## Format d'entrée

```
## [TIMESTAMP ISO 8601] FRÉGATE — ÉVÉNEMENT
- Détail 1
- Détail 2
- SR_CUSTOS validation: PASS / FAIL
```

---

## [2026-06-10T07:59:57Z] INIT — Initialisation de la Flotte SANCTORUM

- Dépôt créé : github.com/kioka8877-ux/SANCTORUM
- Structure des frégates : F01_DOMINION / F02_CELESTIAN / F03_SERAPHIM / SHARED
- CMS initialisé : liber_sanctorum.json — fleet_status: pending_sanctification
- SR_CUSTOS.py : opérationnel
- Axiomes Impériaux : 7 / 7 actifs
- Directive de référence : SANCTORUM_V2_DIRECTIVE_IMPERIALE.pdf
- Que la purification sonore commence.

---

## [2026-06-10T08:05:00Z] CONSTRUCTION — F01_DOMINION : Le Prophète [MANUEL]

- Notebook créé : `F01_DOMINION/CODEBASE/dominion_prophet.ipynb`
- Cellules : 0 (SETUP DRIVE — run once) · 1 (INIT) · 2 (INSTALL) · 3 (SERVEUR) · 4 (INTERFACE Gradio) · 5 (SR_CUSTOS check-in)
- Stack : OmniVoice-Studio · httpx · Gradio (port 7861)
- IN  : reference_vocale.wav + script_text.txt (F01_DOMINION/IN/)
- OUT : voix_brute.wav → F01_DOMINION/OUT/
- Transition fleet_status attendue : → voice_raw_ready
- SR_CUSTOS validation: CONSTRUCTION_PASS

---

## [2026-06-10T08:25:00Z] CONSTRUCTION — F02_CELESTIAN : La Montre [MANUEL]

- Notebook créé : `F02_CELESTIAN/CODEBASE/celestian_watch.ipynb`
- Cellules : 1 (INIT) · 2 (INSTALL) · 3 (INTERFACE Gradio) · 4 (SR_CUSTOS check-in)
- Stack : Spotify Pedalboard · pyloudnorm · Gradio (port 7862)
- Presets créés (4) : standard_voix_purifiee · voix_de_dieu · echo_chamber · micro_aeroport
- Chargement dynamique des presets via importlib (hot-reload possible)
- Pipeline DSP : HighpassFilter → Compressor → Reverb → Presence boost → Noise gate → LUFS normalization
- IN  : voix_brute.wav (F01_DOMINION/OUT/)
- OUT : voix_purifiee.wav → F02_CELESTIAN/OUT/
- Transition fleet_status attendue : → voice_purified_ready
- SR_CUSTOS validation: CONSTRUCTION_PASS

---

## [2026-06-10T08:51:02Z] CONSTRUCTION — F03_SERAPHIM : L'Architecte + La Machine à Micro-jets [MANUEL]

### F03A — seraphim_a_architect.ipynb
- Cellules : 1 (INIT) · 2 (INSTALL) · 3 (INTERFACE Gradio — L'Architecte)
- Stack : librosa>=0.10.0 · matplotlib · pandas · Gradio (port 7862)
- Analyse BPM : `librosa.beat.beat_track` — tempo + beat_frames → beat_times
- Détection sections : MFCC 12 composantes + segmentation agglomérative k = min(6, max(3, dur//15))
- Visualisation : waveform + beat grid + sections colorées (matplotlib Agg, fond #0a0a0f)
- Éditeur timeline Gradio : 9 colonnes (role · start · end · loops · speed · reverse · volume_pct · fade_in_ms · fade_out_ms)
- Rôles disponibles : queue · loop · tete · drop · bridge · outro
- Export directives.json : Drive (F03_CODEBASE/) + repo local + mise à jour liber_sanctorum.json
- Paramètres globaux : crossfade_ms (slider 0-200) · ducking_db (slider -24/0, défaut -14)
- Transition fleet_status attendue : → directives_ready

### F03B — seraphim_b_microjets.ipynb
- Cellules : 1 (INIT) · 2 (INSTALL) · 3 (INTERFACE Gradio — La Machine) · 4 (SR_CUSTOS check-in)
- Stack : pydub · pyrubberband · soundfile · Gradio (port 7863) · apt rubberband-cli
- Time-stretch pitch-preserving : pyrubberband.time_stretch + fallback frame_rate trick pydub
- Ducking dynamique : détection régions actives voix (chunks 50ms, seuil -45 dBFS), rampe fade ±30ms
- Normalisation finale : target dBFS slider (-12 à -1, défaut -3.0 dBFS)
- Formats sortie : mp3 (320k) / wav / flac
- Double export : F03_SERAPHIM/OUT/master_audio_mix.{ext} + SHARED/OUT/final_sanctorum.{ext}
- Prérequis vérifiés à l'INIT : directives.json (F03A) + voix_purifiee.wav (F02) + musique (F03_IN/)
- Transition fleet_status attendue : → audio_ready

### Fichiers support F03
- `directives_template.json` : template 3 segments (queue 0-9s · loop 9-24s ×3 · tete 24-38s)
- `requirements_f03.txt` : librosa · soundfile · numpy · scipy · pandas · matplotlib · pydub · pyrubberband · gradio
- SR_CUSTOS validation: CONSTRUCTION_PASS

---
