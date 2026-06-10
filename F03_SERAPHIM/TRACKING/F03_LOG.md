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

1. **F03A** : Analyser la musique → détecter BPM + sections → éditer timeline → exporter `directives.json` → SR_CUSTOS check-in
2. **F03B** : Lire `directives.json` → découpe chirurgicale → mix avec `voix_purifiee.wav` (ducking) → `master_audio_mix.mp3` → SR_CUSTOS check-in

---

## Phase : CONSTRUCTION

### [2026-06-10T08:51:02Z] CONSTRUCTION TERMINÉE — F03 SERAPHIM COMPLET [MANUEL]

**F03A — L'Architecte (`seraphim_a_architect.ipynb`) — 4 cellules**

| Cellule | Contenu |
|---------|---------|
| 1 INIT | Drive mount · SANCTORUM clone/pull · chemins F03 · makedirs · lecture liber · listing musiques IN/ |
| 2 INSTALL | librosa>=0.10.0 · soundfile · pydub · numpy · scipy · matplotlib · pandas · gradio>=4.31.0 · ffmpeg |
| 3 INTERFACE | Gradio port 7862 · 4 onglets : Analyse Audio / Éditeur Timeline / Prévisualisation JSON / Statut Flotte |
| 4 SR_CUSTOS | check-in --frigate F03A --output directives.json · fleet_status → directives_ready · "PROCHAINE ÉTAPE : F03B" |

**Détail Cellule 3 :**
- `analyze_audio` : BPM (`librosa.beat.beat_track`) + sections MFCC 12 comp. agglomératif k=min(6, max(3, dur//15))
- `plot_analysis` : waveform + beat grid + spans colorés + label sections (matplotlib Agg, fond #0a0a0f)
- Éditeur timeline : DataFrame 9 col. — role / start / end / loops / speed / reverse / volume_pct / fade_in_ms / fade_out_ms
- Rôles : `queue` · `loop` · `tete` · `drop` · `bridge` · `outro`
- `export_directives` : directives.json → Drive F03_CODEBASE/ + repo local /content/SANCTORUM · liber update inline · F03_LOG.md write inline
- Paramètres globaux : crossfade_ms (0–200ms) · ducking_db (-24–0 dB, défaut -14)

**F03B — La Machine à Micro-jets (`seraphim_b_microjets.ipynb`) — 4 cellules**

| Cellule | Contenu |
|---------|---------|
| 1 INIT | Drive mount · SANCTORUM clone/pull · chemins F02+F03+SHARED · makedirs · check prérequis (directives.json, voix_purifiee.wav, musique) |
| 2 INSTALL | pydub · pyrubberband · soundfile · numpy · scipy · matplotlib · gradio>=4.31.0 · ffmpeg · rubberband-cli |
| 3 INTERFACE | Gradio port 7863 · 4 onglets : Assemblage & Mix / Timeline assemblée / Directives JSON / Statut Flotte |
| 4 SR_CUSTOS | check-in --frigate F03B --output master_audio_mix.mp3 · fleet_status → audio_ready · affiche état final flotte |

**Détail Cellule 3 :**
- `_time_stretch` : pyrubberband pitch-preserving + fallback frame_rate trick pydub
- `_duck_music` : détection régions actives voix chunks 50ms, seuil -45 dBFS, rampe fade ±30ms
- `build_music_canvas` : découpe + reverse + speed + volume + fades + loops + crossfade assemblage
- `mix_voice_over_music` : overlay voix sur canvas + padding silence si nécessaire
- `normalize_audio` : target dBFS slider -12 à -1, défaut -3.0 dBFS
- `plot_timeline` : Gantt segments colorés par rôle
- Double export : `F03_SERAPHIM/OUT/master_audio_mix.{ext}` + `SHARED/OUT/final_sanctorum.{ext}`

**Fichiers support**

| Fichier | Rôle |
|---------|------|
| `directives_template.json` | Template 3 segments : queue (0–9s) · loop (9–24s, ×3) · tete (24–38s) |
| `requirements_f03.txt` | librosa · soundfile · numpy · scipy · pandas · matplotlib · pydub · pyrubberband · gradio |

---

## Historique des missions

*(Généré automatiquement par seraphim_a_architect.ipynb et seraphim_b_microjets.ipynb lors de l'exécution)*
