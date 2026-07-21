#!/usr/bin/env python3
"""
F00a — CLEANSE
Lit config.json, isole la voix (demucs) et nettoie le bruit (noisereduce).
Output: ref_voice_isolated.wav

Usage:
    python3 cleanse.py config.json [source_audio_path]
    
Si source_audio_path n'est pas fourni, utilise le champ "source" du config.json.
"""

import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path


def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_demucs(input_audio, output_dir):
    """
    Isole la voix avec demucs (htdemucs model).
    Output: {output_dir}/htdemucs/{stem_name}/vocals.wav
    """
    print(f"[DEMUCS] Isolation vocale de {input_audio}...")
    
    # Install demucs if not present
    try:
        import demucs
    except ImportError:
        print("[DEMUCS] Installation...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'demucs', '-q'], check=True)
    
    cmd = [
        sys.executable, '-m', 'demucs',
        '--two-stems', 'vocals',      # Only separate vocals vs rest
        '-n', 'htdemucs',              # Best model
        '-o', output_dir,
        input_audio
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print(f"[DEMUCS] ERREUR: {result.stderr}")
        raise RuntimeError(f"Demucs failed: {result.stderr}")
    
    # Find the vocals output
    stem_name = Path(input_audio).stem
    vocals_path = Path(output_dir) / 'htdemucs' / stem_name / 'vocals.wav'
    
    if not vocals_path.exists():
        raise FileNotFoundError(f"Demucs output not found at {vocals_path}")
    
    print(f"[DEMUCS] Voix isolée: {vocals_path}")
    return str(vocals_path)


def run_noisereduce(input_wav, output_wav):
    """
    Réduit le bruit statique avec noisereduce.
    """
    print(f"[NOISEREDUCE] Nettoyage de {input_wav}...")
    
    try:
        import noisereduce
    except ImportError:
        print("[NOISEREDUCE] Installation...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'noisereduce', '-q'], check=True)
    
    import librosa
    import soundfile as sf
    import numpy as np
    
    # Load audio
    y, sr = librosa.load(input_wav, sr=24000, mono=True)
    
    # Use first 0.5s as noise profile (or first 0.5s of the audio)
    # If audio is very short, use the whole thing
    noise_len = min(int(0.5 * sr), len(y) // 4)
    noise_profile = y[:noise_len]
    
    # Apply noisereduce
    reduced = noisereduce.reduce_noise(
        y=y,
        sr=sr,
        y_noise=noise_profile,
        stationary=True,
        prop_decrease=0.8
    )
    
    # Save
    sf.write(output_wav, reduced, sr)
    print(f"[NOISEREDUCE] Audio nettoyé: {output_wav}")
    return output_wav


def trim_segment(input_wav, output_wav, start_sec, end_sec):
    """
    Trim l'audio au segment choisi avec ffmpeg.
    """
    print(f"[TRIM] Segment {start_sec}s → {end_sec}s...")
    
    duration = end_sec - start_sec
    cmd = [
        'ffmpeg', '-y',
        '-i', input_wav,
        '-ss', str(start_sec),
        '-t', str(duration),
        '-ar', '24000',
        '-ac', '1',
        output_wav
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"[TRIM] ffmpeg stderr: {result.stderr}")
        raise RuntimeError(f"ffmpeg trim failed: {result.stderr}")
    
    print(f"[TRIM] Segment extrait: {output_wav}")
    return output_wav


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cleanse.py config.json [source_audio_path]")
        sys.exit(1)
    
    config_path = sys.argv[1]
    config = load_config(config_path)
    
    # Resolve source audio path
    if len(sys.argv) >= 3:
        source_path = sys.argv[2]
    else:
        source_path = config.get('source', 'ref_raw.mp3')
    
    if not os.path.exists(source_path):
        print(f"[ERROR] Fichier source introuvable: {source_path}")
        sys.exit(1)
    
    # Output paths
    output_dir = os.path.dirname(source_path) or '.'
    isolated_path = os.path.join(output_dir, 'ref_voice_isolated.wav')
    cleaned_path = os.path.join(output_dir, 'ref_voice_clean_forge.wav')
    
    segment = config.get('segment', {})
    start_sec = segment.get('start', 0)
    end_sec = segment.get('end', 20)
    
    # Step 1: Trim to segment first (faster than demucs on full audio)
    print(f"\n=== F00a CLEANSE ===")
    print(f"Source: {source_path}")
    print(f"Segment: {start_sec}s → {end_sec}s ({end_sec - start_sec:.1f}s)")
    
    trimmed_path = os.path.join(output_dir, '_trimmed_raw.wav')
    trim_segment(source_path, trimmed_path, start_sec, end_sec)
    
    # Step 2: Vocal isolation (demucs) on the trimmed segment
    if config.get('vocal_isolation', True):
        with tempfile.TemporaryDirectory() as tmpdir:
            vocals_path = run_demucs(trimmed_path, tmpdir)
            
            # Step 3: Denoise
            if config.get('denoise', True):
                run_noisereduce(vocals_path, isolated_path)
            else:
                # Just copy the isolated vocals
                import shutil
                shutil.copy2(vocals_path, isolated_path)
    else:
        # No vocal isolation, just denoise if requested
        if config.get('denoise', True):
            run_noisereduce(trimmed_path, isolated_path)
        else:
            # Just copy the trimmed audio
            import shutil
            shutil.copy2(trimmed_path, isolated_path)
    
    # Cleanup temp
    if os.path.exists(trimmed_path):
        os.remove(trimmed_path)
    
    print(f"\n✅ CLEANSE terminé: {isolated_path}")
    print(f"   → Prêt pour F00b FORGE")
    
    return isolated_path


if __name__ == '__main__':
    main()
