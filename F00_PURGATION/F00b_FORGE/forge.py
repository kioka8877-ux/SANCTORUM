#!/usr/bin/env python3
"""
F00b — FORGE
Lit ref_voice_isolated.wav (produit par F00a CLEANSE) + config.json,
ajuste la vitesse et produit ref_voice_clean.wav prêt pour F01_DOMINION.

Usage:
    python3 forge.py config.json [isolated_wav_path]
    
Si isolated_wav_path n'est pas fourni, utilise ref_voice_isolated.wav dans le même dossier.
"""

import json
import os
import sys
import subprocess
from pathlib import Path


def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def adjust_speed(input_wav, output_wav, speed):
    """
    Ajuste la vitesse avec ffmpeg atempo.
    speed > 1.0 = plus rapide, speed < 1.0 = plus lent.
    ffmpeg atempo accepte 0.5 à 2.0 directement.
    Pour aller au-delà, il faut chaîner plusieurs atempo.
    """
    print(f"[FORGE] Ajustement vitesse: {speed}x...")
    
    # Build atempo filter chain
    atempo_filters = []
    remaining = speed
    while remaining > 2.0:
        atempo_filters.append('atempo=2.0')
        remaining /= 2.0
    while remaining < 0.5:
        atempo_filters.append('atempo=0.5')
        remaining /= 0.5
    atempo_filters.append(f'atempo={remaining:.4f}')
    
    filter_chain = ','.join(atempo_filters)
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_wav,
        '-filter:a', filter_chain,
        '-ar', '24000',
        '-ac', '1',
        output_wav
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"[FORGE] ffmpeg stderr: {result.stderr}")
        raise RuntimeError(f"ffmpeg speed adjust failed: {result.stderr}")
    
    print(f"[FORGE] Vitesse ajustée: {output_wav}")
    return output_wav


def normalize_audio(input_wav, output_wav):
    """
    Normalise le volume avec ffmpeg loudnorm (broadcast standard).
    """
    print(f"[FORGE] Normalisation volume...")
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_wav,
        '-filter:a', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        '-ar', '24000',
        '-ac', '1',
        output_wav
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"[FORGE] ffmpeg stderr: {result.stderr}")
        # Fallback: just copy
        import shutil
        shutil.copy2(input_wav, output_wav)
        print(f"[FORGE] Normalisation échouée, copie directe: {output_wav}")
    else:
        print(f"[FORGE] Normalisé: {output_wav}")
    
    return output_wav


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 forge.py config.json [isolated_wav_path]")
        sys.exit(1)
    
    config_path = sys.argv[1]
    config = load_config(config_path)
    
    # Resolve input wav (output of F00a CLEANSE)
    if len(sys.argv) >= 3:
        input_wav = sys.argv[2]
    else:
        input_wav = 'ref_voice_isolated.wav'
    
    if not os.path.exists(input_wav):
        print(f"[ERROR] Fichier isolé introuvable: {input_wav}")
        print(f"        Lance d'abord F00a CLEANSE pour produire ref_voice_isolated.wav")
        sys.exit(1)
    
    speed = config.get('speed', 1.0)
    
    # Output path
    output_dir = os.path.dirname(input_wav) or '.'
    final_output = os.path.join(output_dir, 'ref_voice_clean.wav')
    
    print(f"\n=== F00b FORGE ===")
    print(f"Input: {input_wav}")
    print(f"Speed: {speed}x")
    
    # Step 1: Speed adjustment
    if speed != 1.0:
        speed_path = os.path.join(output_dir, '_speed_adjusted.wav')
        adjust_speed(input_wav, speed_path, speed)
    else:
        speed_path = input_wav
    
    # Step 2: Normalize volume
    normalize_audio(speed_path, final_output)
    
    # Cleanup temp
    if speed_path != input_wav and os.path.exists(speed_path):
        os.remove(speed_path)
    
    # Print file info
    file_size = os.path.getsize(final_output)
    print(f"\n✅ FORGE terminé: {final_output}")
    print(f"   Taille: {file_size / 1024:.1f} KB")
    print(f"   → Prêt pour F01_DOMINION (model_prep.py)")
    
    return final_output


if __name__ == '__main__':
    main()
