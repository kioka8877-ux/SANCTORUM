"""
Preset : voix_de_dieu
Description : Grave, puissante, présence souveraine.
              Highpass 60Hz / Compressor 4:1 / -12dB / Reverb room=0.45 wet=0.20
"""
import numpy as np
from pedalboard import Pedalboard, HighpassFilter, Compressor, Reverb
from pydub import AudioSegment


PRESET_NAME = "voix_de_dieu"
PRESET_DESCRIPTION = "Grave et souveraine — impact lourd, présence divine"


def apply(audio_segment: AudioSegment) -> AudioSegment:
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    sample_rate = audio_segment.frame_rate

    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).T
    else:
        samples = samples.reshape((1, -1))

    samples /= 32768.0

    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=60.0),
        Compressor(threshold_db=-12.0, ratio=4.0, attack_ms=3.0, release_ms=150.0),
        Reverb(room_size=0.45, wet_level=0.20, dry_level=0.80, damping=0.3),
    ])

    processed = board(samples, sample_rate)
    processed = np.clip(processed * 32768.0, -32768, 32767).astype(np.int16)

    if processed.ndim == 2:
        processed = processed.T.flatten()

    return audio_segment._spawn(processed.tobytes())
