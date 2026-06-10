"""
Preset : echo_chamber
Description : Répétition spatiale, profondeur sonore.
              Highpass 80Hz / Delay 250ms / Reverb room=0.30 wet=0.25
"""
import numpy as np
from pedalboard import Pedalboard, HighpassFilter, Reverb, Delay
from pydub import AudioSegment


PRESET_NAME = "echo_chamber"
PRESET_DESCRIPTION = "Écho spatial — profondeur et répétition ambiante"


def apply(audio_segment: AudioSegment) -> AudioSegment:
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    sample_rate = audio_segment.frame_rate

    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).T
    else:
        samples = samples.reshape((1, -1))

    samples /= 32768.0

    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=80.0),
        Delay(delay_seconds=0.25, feedback=0.4, mix=0.3),
        Reverb(room_size=0.30, wet_level=0.25, dry_level=0.75, damping=0.4),
    ])

    processed = board(samples, sample_rate)
    processed = np.clip(processed * 32768.0, -32768, 32767).astype(np.int16)

    if processed.ndim == 2:
        processed = processed.T.flatten()

    return audio_segment._spawn(processed.tobytes())
