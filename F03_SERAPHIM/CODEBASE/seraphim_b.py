"""
seraphim_b.py — F03B SERAPHIM-B : La Machine a Micro-jets
Assemble le mix final : musique (directives.json) + voix off → master_audio_mix_XXX.mp3
Push vers ANGRON-V2 F02_LACERAT/IN/
"""
import argparse, json, os, sys, math, base64, urllib.request


def assemble_mix(directives_path, music_path, voice_path, output_path):
    from pydub import AudioSegment

    with open(directives_path) as f:
        d = json.load(f)

    print(f"[SERAPHIM-B] BPM={d['bpm']} | {len(d['audio_timeline'])} segments | ducking={d['ducking_db']}dB")

    music_src = AudioSegment.from_file(music_path).set_frame_rate(44100).set_channels(2)
    voice     = AudioSegment.from_file(voice_path).set_frame_rate(44100).set_channels(2)

    crossfade_ms = d.get('crossfade_ms', 15)
    music_backbone = AudioSegment.silent(duration=0)

    for seg in d['audio_timeline']:
        start_ms = int(seg['start'] * 1000)
        end_ms   = int(seg['end']   * 1000)
        clip = music_src[start_ms:end_ms]

        # Speed
        speed = seg.get('speed', 1.0)
        if speed != 1.0:
            clip = clip._spawn(
                clip.raw_data,
                overrides={"frame_rate": int(clip.frame_rate * speed)}
            ).set_frame_rate(44100)

        # Reverse
        if seg.get('reverse', False):
            clip = clip.reverse()

        # Volume
        vol_pct = seg.get('volume_pct', 100)
        if vol_pct != 100 and vol_pct > 0:
            clip = clip + (20 * math.log10(vol_pct / 100))

        # Fades
        fi = seg.get('fade_in_ms', 0)
        fo = seg.get('fade_out_ms', 0)
        if fi > 0:
            clip = clip.fade_in(min(fi, len(clip) // 2))
        if fo > 0:
            clip = clip.fade_out(min(fo, len(clip) // 2))

        # Loops
        looped = clip
        for _ in range(seg.get('loops', 1) - 1):
            looped = looped.append(clip, crossfade=crossfade_ms)

        if len(music_backbone) == 0:
            music_backbone = looped
        else:
            music_backbone = music_backbone.append(looped, crossfade=crossfade_ms)

    print(f"[SERAPHIM-B] Backbone musique : {len(music_backbone)/1000:.1f}s")

    # Stretch backbone to cover voice + 2s tail
    target_ms = len(voice) + 2000
    if len(music_backbone) < target_ms:
        last = d['audio_timeline'][-1]
        filler = music_src[int(last['start']*1000):int(last['end']*1000)]
        if len(filler) == 0:
            filler = music_src[:4000]
        while len(music_backbone) < target_ms:
            music_backbone = music_backbone.append(filler, crossfade=crossfade_ms)

    music_backbone = music_backbone[:target_ms]

    # Ducking : full volume pendant hook (avant voix), duck sous la voix
    ducking_db  = d.get('ducking_db', -14.0)
    music_ducked = music_backbone + ducking_db

    # Hook duration = 500ms plein volume avant que la voix commence
    hook_ms = 500
    if len(music_backbone) > hook_ms:
        music_final = music_backbone[:hook_ms].append(music_ducked[hook_ms:], crossfade=50)
    else:
        music_final = music_ducked

    # Pad si necessaire
    if len(music_final) < len(voice):
        music_final = music_final + AudioSegment.silent(len(voice) - len(music_final))

    # Mix voix sur musique
    master = music_final.overlay(voice, position=0)
    master = master.normalize(headroom=1.0)

    master.export(output_path, format='mp3', bitrate='192k')
    size_kb = os.path.getsize(output_path) // 1024
    dur_s   = len(master) / 1000
    print(f"[SERAPHIM-B] master_audio_mix -> {output_path} ({size_kb} KB, {dur_s:.1f}s)")

    # Export backbone seul (musique sans voix) — pour reutilisation dans d'autres projets
    backbone_path = output_path.replace('.mp3', '_backbone.mp3')
    music_backbone_full = music_backbone[:target_ms].normalize(headroom=1.0)
    music_backbone_full.export(backbone_path, format='mp3', bitrate='192k')
    size_kb2 = os.path.getsize(backbone_path) // 1024
    print(f"[SERAPHIM-B] music_backbone   -> {backbone_path} ({size_kb2} KB, {dur_s:.1f}s)")

    return dur_s, backbone_path


def push_to_angron(local_path, project_id, gh_token, repo="kioka8877-ux/ANGRON-V2", dest_filename=None):
    filename  = dest_filename or f"master_audio_mix_{project_id}.mp3"
    dest_path = f"F02_LACERAT/IN/{filename}"
    api_url   = f"https://api.github.com/repos/{repo}/contents/{dest_path}"

    with open(local_path, 'rb') as f:
        content_b64 = base64.b64encode(f.read()).decode()

    headers = {
        "Authorization": f"token {gh_token}",
        "Accept":        "application/vnd.github+json",
        "Content-Type":  "application/json"
    }

    # GET sha si le fichier existe deja
    sha = ""
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req) as r:
            sha = json.loads(r.read()).get('sha', '')
    except Exception:
        pass

    payload = {
        "message": f"[SERAPHIM] {filename}",
        "content": content_b64,
        "branch":  "main"
    }
    if sha:
        payload["sha"] = sha

    req2 = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode(),
        headers=headers,
        method="PUT"
    )
    with urllib.request.urlopen(req2) as r:
        result = json.loads(r.read())
    print(f"[SERAPHIM-B] Pousse -> {repo}/{dest_path}")
    print(f"[SERAPHIM-B] Commit : {result['commit']['sha'][:8]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--directives',  required=True)
    p.add_argument('--music',       required=True)
    p.add_argument('--voice',       required=True)
    p.add_argument('--output',      required=True)
    p.add_argument('--project-id',  required=True)
    p.add_argument('--push',        action='store_true')
    args = p.parse_args()

    _, backbone_path = assemble_mix(args.directives, args.music, args.voice, args.output)

    if args.push:
        gh_token = os.environ.get('GH_PAT')
        if not gh_token:
            print("[SERAPHIM-B] ERREUR: GH_PAT manquant", file=sys.stderr)
            sys.exit(1)
        # Pousse le mix final (voix + musique)
        push_to_angron(args.output, args.project_id, gh_token)
        # Pousse le backbone seul (musique pure, sans voix)
        push_to_angron(backbone_path, args.project_id, gh_token,
                       dest_filename=f"music_backbone_{args.project_id}.mp3")


if __name__ == '__main__':
    main()

