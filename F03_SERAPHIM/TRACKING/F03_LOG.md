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

## Historique des missions

*(Généré automatiquement par seraphim_a_architect.ipynb et seraphim_b_microjets.ipynb)*
