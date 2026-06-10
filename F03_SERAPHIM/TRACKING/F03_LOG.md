# F03_SERAPHIM — Journal de Mission

> Frégate SERAPHIM — L'Architecte (F03A) + La Machine à Micro-jets (F03B)
> Pipeline : trend_music.mp3 → directives.json → master_audio_mix.mp3

| Champ | Valeur |
|-------|--------|
| Frégate A | F03A — L'Architecte |
| Frégate B | F03B — La Machine à Micro-jets |
| Moteur analyse | Librosa (BPM + structure) |
| Moteur découpe | Pydub + pyrubberband |
| Interface | Gradio headless |

## Workflow

1. **F03A** : Analyser la musique → détecter BPM + sections → éditer timeline → exporter `directives.json`
2. **F03B** : Lire `directives.json` → découpe chirurgicale → mix avec `voix_purifiee.wav` (ducking) → `master_audio_mix.mp3`

---

## Phase : CONSTRUCTION

### [2026-06-10T08:51:02Z] CONSTRUCTION TERMINÉE [MANUEL]

**F03A — L'Architecte (`seraphim_a_architect.ipynb`)**

| Élément | Détail |
|---------|--------|
| Cellules | 1 INIT · 2 INSTALL · 3 INTERFACE Gradio (port 7862) |
| BPM | `librosa.beat.beat_track` → tempo + beat_times (64 beats max affichés) |
| Sections | MFCC 12 comp. + segmentation agglomérative, k = min(6, max(3, dur//15)) |
| Visualisation | Waveform + beat grid + spans colorés par section (matplotlib Agg) |
| Timeline editor | DataFrame 9 col. — role / start / end / loops / speed / reverse / volume_pct / fade_in_ms / fade_out_ms |
| Rôles | `queue` · `loop` · `tete` · `drop` · `bridge` · `outro` |
| Params globaux | crossfade_ms (0–200ms) · ducking_db (-24–0 dB, défaut -14) |
| Export | directives.json → Drive F03_CODEBASE/ + repo local /content/SANCTORUM |
| Liber update | fleet_status → `directives_ready` · f03_seraphim.status → `directives_ready` |

**F03B — La Machine à Micro-jets (`seraphim_b_microjets.ipynb`)**

| Élément | Détail |
|---------|--------|
| Cellules | 1 INIT · 2 INSTALL · 3 INTERFACE Gradio (port 7863) · 4 SR_CUSTOS check-in |
| Prérequis INIT | directives.json (F03A) + voix_purifiee.wav (F02_OUT/) + musique (F03_IN/) |
| Time-stretch | pyrubberband.time_stretch (pitch-preserving) — fallback frame_rate trick pydub |
| Ducking | Détection régions actives voix chunks 50ms, seuil -45 dBFS, rampe fade ±30ms |
| Normalisation | normalize_audio(target_dbfs) — slider -12 à -1, défaut -3.0 dBFS |
| Sortie | mp3 (320k) / wav / flac |
| Double export | F03_SERAPHIM/OUT/master_audio_mix.{ext} + SHARED/OUT/final_sanctorum.{ext} |
| Liber update | fleet_status → `audio_ready` · f03_seraphim.status → `done` · final_output → SHARED/OUT/final_sanctorum |

**Fichiers support créés**

| Fichier | Rôle |
|---------|------|
| `directives_template.json` | Template 3 segments : queue (0–9s) · loop (9–24s, ×3) · tete (24–38s) |
| `requirements_f03.txt` | librosa · soundfile · numpy · scipy · pandas · matplotlib · pydub · pyrubberband · gradio |

---

## Historique des missions

*(Généré automatiquement par seraphim_a_architect.ipynb et seraphim_b_microjets.ipynb lors de l'exécution)*
