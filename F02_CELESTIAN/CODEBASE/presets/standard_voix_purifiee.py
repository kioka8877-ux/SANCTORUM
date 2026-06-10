"""
Preset : standard_voix_purifiee
Description : Preset par défaut. Specs Directive Impériale V2.
              Highpass 75Hz / Compressor 3.5:1 / -15dB / Reverb room=0.20 wet=0.08
"""
import numpy as np
from pedalboard import Pedalboard, HighpassFilter, Compressor, Reverb
from pydub import AudioSegment
import soundfile as sf
import io


PRESET_NAME = "standard_voix_purifiee"
PRESET_DESCRIPTION = "Voix purifiée standard — specs Directive Impériale"


def apply(audio_segment: AudioSegment) -> AudioSegment:
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    sample_rate = audio_segment.frame_rate

    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).T
    else:
        samples = samples.reshape((1, -1))

    samples /= 32768.0

    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=75.0),
        Compressor(threshold_db=-15.0, ratio=3.5, attack_ms=5.0, release_ms=100.0),
        Reverb(room_size=0.20, wet_level=0.08, dry_level=0.92, damping=0.5),
    ])

    processed = board(samples, sample_rate)
    processed = np.clip(processed * 32768.0, -32768, 32767).astype(np.int16)

    if processed.ndim == 2:
        processed = processed.T.flatten()

    return audio_segment._spawn(processed.tobytes())
