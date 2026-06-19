"""
seraphim_a.py — F03A SERAPHIM-A : Architecte JSON
Phase analyze : BPM detection + viewer HTML pour l'operateur
Phase oracle  : Claude enrichit les segments choisis → directives.json
"""
import argparse, json, os, sys, base64, io, math

def analyze_bpm(music_path, output_json, output_html):
    import librosa
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    print(f"[SERAPHIM-A] Chargement {music_path}")
    y, sr = librosa.load(music_path, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr).tolist()
    bpm = float(f"{tempo:.2f}")

    fig, ax = plt.subplots(figsize=(16, 4), facecolor='#0d0d1a')
    times = np.linspace(0, duration, len(y))
    ax.plot(times, y, color='#58C4DD', alpha=0.6, linewidth=0.3)
    for bt in beat_times[:200]:
        ax.axvline(x=bt, color='#FFF1B6', alpha=0.25, linewidth=0.4)
    ax.set_facecolor('#0d0d1a')
    ax.tick_params(colors='#ECEFF1')
    ax.set_xlabel('Secondes', color='#ECEFF1')
    ax.set_title(f'BPM: {bpm} | Duree: {duration:.1f}s | Beats: {len(beat_times)}', color='#58C4DD', fontsize=13)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#0d0d1a')
    plt.close()
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    analysis = {
        "music_file": os.path.basename(music_path),
        "bpm": bpm,
        "duration_sec": round(duration, 2),
        "beat_count": len(beat_times),
        "beat_times_sample": [round(t, 3) for t in beat_times[:60]]
    }
    with open(output_json, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"[SERAPHIM-A] Analyse OK — BPM={bpm} Duree={duration:.1f}s")

    html = _build_html(analysis, img_b64)
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[SERAPHIM-A] Viewer HTML -> {output_html}")
    return analysis


def _build_html(a, img_b64):
    beats_js = json.dumps(a['beat_times_sample'])
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SERAPHIM — {a['music_file']}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d0d1a;color:#ECEFF1;font-family:'Courier New',monospace;padding:24px}}
h1{{color:#58C4DD;font-size:1.4em;margin-bottom:8px}}
.stats{{display:flex;gap:28px;margin:12px 0;color:#FFF1B6;font-size:1.05em}}
.waveform{{width:100%;border:1px solid #2a2a3e;margin:20px 0}}
.box{{background:#13132a;border:1px solid #2a2a3e;padding:20px;margin:18px 0;border-radius:8px}}
h2{{color:#A6CF98;margin-bottom:14px;font-size:1.1em}}
table{{width:100%;border-collapse:collapse}}
th{{background:#1e1e38;color:#58C4DD;padding:10px;text-align:left;font-size:.9em}}
td{{padding:9px 10px;border-bottom:1px solid #252540;vertical-align:middle}}
.q{{color:#58C4DD;font-weight:bold}} .l{{color:#A6CF98;font-weight:bold}} .t{{color:#FFF1B6;font-weight:bold}}
input[type=number]{{background:#1e1e38;border:1px solid #444;color:#ECEFF1;padding:5px 8px;width:85px;border-radius:4px;font-family:'Courier New',monospace}}
.btn{{background:#58C4DD;color:#0d0d1a;border:none;padding:9px 18px;cursor:pointer;border-radius:4px;font-family:'Courier New',monospace;font-weight:bold;margin-top:14px;margin-right:8px}}
.btn:hover{{background:#FFF1B6}}
.out{{background:#070714;border:1px solid #58C4DD;padding:14px;border-radius:6px;font-size:.88em;white-space:pre-wrap;color:#A6CF98;margin-top:12px;min-height:60px}}
.beats{{color:#90A4AE;font-size:.8em;line-height:1.9em}}
</style>
</head>
<body>
<h1>SERAPHIM VIEWER — {a['music_file']}</h1>
<div class="stats">
  <span>BPM : <strong>{a['bpm']}</strong></span>
  <span>Duree : <strong>{a['duration_sec']}s</strong></span>
  <span>Beats : <strong>{a['beat_count']}</strong></span>
</div>
<img class="waveform" src="data:image/png;base64,{img_b64}" alt="Waveform">

<div class="box">
  <h2>Choisir les segments</h2>
  <p style="color:#90A4AE;font-size:.88em;margin-bottom:14px">
    Ecoute la musique et place les bornes. Clique "Generer JSON" pour obtenir le payload.
  </p>
  <table>
    <tr><th>Role</th><th>Start (s)</th><th>End (s)</th><th>Description</th></tr>
    <tr>
      <td><span class="q">QUEUE</span><br><small style="color:#666">intro / montee</small></td>
      <td><input type="number" id="qs" value="0.0" step="0.5" min="0" max="{a['duration_sec']}"></td>
      <td><input type="number" id="qe" value="9.0" step="0.5" min="0" max="{a['duration_sec']}"></td>
      <td style="color:#90A4AE;font-size:.85em">Energie 100% — hook video</td>
    </tr>
    <tr>
      <td><span class="l">LOOP</span><br><small style="color:#666">section centrale</small></td>
      <td><input type="number" id="ls" value="9.0" step="0.5" min="0" max="{a['duration_sec']}"></td>
      <td><input type="number" id="le" value="24.0" step="0.5" min="0" max="{a['duration_sec']}"></td>
      <td style="color:#90A4AE;font-size:.85em">Energie 80% — sous la voix off</td>
    </tr>
    <tr>
      <td><span class="t">TETE</span><br><small style="color:#666">finale / drop</small></td>
      <td><input type="number" id="ts" value="24.0" step="0.5" min="0" max="{a['duration_sec']}"></td>
      <td><input type="number" id="te" value="38.0" step="0.5" min="0" max="{a['duration_sec']}"></td>
      <td style="color:#90A4AE;font-size:.85em">Energie 110% — CTA final</td>
    </tr>
  </table>
  <button class="btn" onclick="gen()">Generer JSON</button>
  <button class="btn" onclick="copy()" style="background:#A6CF98">Copier</button>
  <div class="out" id="out">→ Clique sur Generer JSON</div>
</div>

<div class="box">
  <h2>Beats detectes (30 premiers)</h2>
  <div class="beats" id="beatrow"></div>
</div>

<script>
const beats = {beats_js};
document.getElementById('beatrow').innerHTML = beats.slice(0,30).map(t => '<span style="color:#58C4DD">'+t.toFixed(2)+'s</span>').join(' | ');

function gen() {{
  const seg = [
    {{"role":"queue","start":+document.getElementById('qs').value,"end":+document.getElementById('qe').value}},
    {{"role":"loop", "start":+document.getElementById('ls').value,"end":+document.getElementById('le').value}},
    {{"role":"tete", "start":+document.getElementById('ts').value,"end":+document.getElementById('te').value}}
  ];
  document.getElementById('out').textContent = JSON.stringify(seg);
}}

function copy() {{
  const t = document.getElementById('out').textContent;
  if(t.startsWith('→')) {{ alert('Genere le JSON dabord'); return; }}
  navigator.clipboard.writeText(t).then(() => alert('JSON copie !'));
}}
</script>
</body>
</html>"""


def oracle_enrich(analysis_json, segments_str, script_path, whisper_path, output_directives):
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[SERAPHIM-A] ERREUR: ANTHROPIC_API_KEY manquant", file=sys.stderr)
        sys.exit(1)

    with open(analysis_json) as f:
        analysis = json.load(f)

    segments = json.loads(segments_str)

    script_text = open(script_path).read()[:3000] if script_path and os.path.exists(script_path) else "(script non fourni)"
    whisper_text = open(whisper_path).read()[:2000] if whisper_path and os.path.exists(whisper_path) else "(timestamps non fournis)"

    prompt = f"""Tu es SERAPHIM, architecte sonore de la flotte ANGRON.

DONNEES MUSICALES :
- Fichier : {analysis['music_file']}
- BPM : {analysis['bpm']}
- Duree totale : {analysis['duration_sec']}s

SEGMENTS CHOISIS PAR L'OPERATEUR :
{json.dumps(segments, indent=2)}

SCRIPT VOCAL :
{script_text}

TIMESTAMPS WHISPER :
{whisper_text}

MISSION : enrichir les segments avec des parametres audio precis.
Decides pour chaque segment :
- volume_pct (75-115) selon l'energie du moment script
- fade_in_ms (0-300)
- fade_out_ms (0-600)
- loops (1-4)
- speed (0.9-1.1)
- reverse (toujours false pour un short)

REGLES :
- QUEUE : fort (95-110%), fade_out doux (200ms), loops=1 — hook pur
- LOOP : duck-friendly (75-85%), fade symetrique (50ms), loops 2-3 selon duree voix
- TETE : climax (105-115%), fade_out long (400ms+), loops=1 — drop final CTA

Reponds UNIQUEMENT avec un JSON valide, exactement ce format :
{{
  "source_music": "{analysis['music_file']}",
  "bpm": {analysis['bpm']},
  "total_duration_sec": {analysis['duration_sec']},
  "audio_timeline": [
    {{"role":"queue","start":0,"end":0,"loops":1,"speed":1.0,"reverse":false,"volume_pct":100,"fade_in_ms":0,"fade_out_ms":200}},
    {{"role":"loop","start":0,"end":0,"loops":2,"speed":1.0,"reverse":false,"volume_pct":80,"fade_in_ms":50,"fade_out_ms":50}},
    {{"role":"tete","start":0,"end":0,"loops":1,"speed":1.0,"reverse":false,"volume_pct":110,"fade_in_ms":0,"fade_out_ms":400}}
  ],
  "crossfade_ms": 15,
  "ducking_db": -14.0
}}
Aucun texte avant ou apres le JSON."""

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = resp.content[0].text.strip()
    if '```' in raw:
        parts = raw.split('```')
        raw = parts[1] if len(parts) > 1 else parts[0]
        if raw.startswith('json'):
            raw = raw[4:].strip()

    directives = json.loads(raw)

    # Merge operator segment timestamps into oracle result
    op_map = {s['role']: s for s in segments}
    for seg in directives['audio_timeline']:
        role = seg['role']
        if role in op_map:
            seg['start'] = op_map[role]['start']
            seg['end'] = op_map[role]['end']

    with open(output_directives, 'w') as f:
        json.dump(directives, f, indent=2, ensure_ascii=False)
    print(f"[SERAPHIM-A] Oracle OK → {output_directives}")
    for seg in directives['audio_timeline']:
        print(f"  {seg['role']:6} vol={seg['volume_pct']}% loops={seg['loops']} fade_out={seg['fade_out_ms']}ms")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--phase', choices=['analyze', 'oracle'], required=True)
    p.add_argument('--music')
    p.add_argument('--output-json', default='/tmp/seraphim_analysis.json')
    p.add_argument('--output-html', default='/tmp/seraphim_viewer.html')
    p.add_argument('--analysis-json')
    p.add_argument('--segments')
    p.add_argument('--script', default='')
    p.add_argument('--whisper', default='')
    p.add_argument('--output-directives', default='/tmp/directives.json')
    args = p.parse_args()

    if args.phase == 'analyze':
        if not args.music:
            print("--music requis", file=sys.stderr); sys.exit(1)
        analyze_bpm(args.music, args.output_json, args.output_html)
    elif args.phase == 'oracle':
        if not args.analysis_json or not args.segments:
            print("--analysis-json et --segments requis", file=sys.stderr); sys.exit(1)
        oracle_enrich(args.analysis_json, args.segments, args.script, args.whisper, args.output_directives)


if __name__ == '__main__':
    main()
