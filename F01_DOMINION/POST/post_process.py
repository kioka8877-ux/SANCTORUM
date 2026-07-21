#!/usr/bin/env python3
"""
F01 POST — post_process.py
Lit post_config.json, applique ffmpeg atempo pour ralentir/accélérer l'audio final.

Usage:
    python3 post_process.py post_config.json [input_mp3]
    
Si input_mp3 n'est pas fourni, utilise "source" du config.json.
"""

import json
import os
import sys
import subprocess


def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def adjust_speed(input_mp3, output_mp3, speed):
    """
    Ajuste la vitesse avec ffmpeg atempo.
    speed < 1.0 = ralentir, speed > 1.0 = accélérer.
    """
    print(f"[POST] Ajustement vitesse: {speed}x sur {input_mp3}...")

    # Build atempo filter chain (atempo accepts 0.5-2.0 per filter)
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
        '-i', input_mp3,
        '-filter:a', filter_chain,
        '-b:a', '192k',
        output_mp3
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"[POST] ffmpeg stderr: {result.stderr}")
        raise RuntimeError(f"ffmpeg speed adjust failed: {result.stderr}")

    print(f"[POST] Vitesse ajustée: {output_mp3}")
    return output_mp3


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 post_process.py post_config.json [input_mp3]")
        sys.exit(1)

    config_path = sys.argv[1]
    config = load_config(config_path)

    # Resolve input
    if len(sys.argv) >= 3:
        input_mp3 = sys.argv[2]
    else:
        input_mp3 = config.get('source', 'output.mp3')

    if not os.path.exists(input_mp3):
        print(f"[ERROR] Fichier introuvable: {input_mp3}")
        sys.exit(1)

    speed = config.get('speed', 1.0)

    # Output path
    output_dir = os.path.dirname(input_mp3) or '.'
    base_name = os.path.splitext(os.path.basename(input_mp3))[0]
    output_mp3 = os.path.join(output_dir, f'{base_name}_post.mp3')

    print(f"\n=== F01 POST ===")
    print(f"Input: {input_mp3}")
    print(f"Speed: {speed}x")
    print(f"Output: {output_mp3}")

    # Apply speed
    adjust_speed(input_mp3, output_mp3, speed)

    # File info
    file_size = os.path.getsize(output_mp3)
    print(f"\n✅ POST terminé: {output_mp3}")
    print(f"   Taille: {file_size / 1024:.1f} KB")

    return output_mp3


if __name__ == '__main__':
    main()
