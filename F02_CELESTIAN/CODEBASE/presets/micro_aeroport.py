"""
Preset : micro_aeroport
Description : Bande passante filtrée, couleur annonce publique.
              Bandpass 300Hz–3kHz / Légère saturation / Compressor 5:1 / -10dB
"""
import numpy as np
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Compressor, Distortion
from pydub import AudioSegment


PRESET_NAME = "micro_aeroport"
PRESET_DESCRIPTION = "Annonce publique — bande filtrée, saturation légère"

PRESET_DEFAULTS = {
    'highpass_hz'     : 300.0,
    'comp_threshold'  : -10.0,
    'comp_ratio'      : 5.0,
    'reverb_room'     : 0.05,
    'reverb_wet'      : 0.02,
}


def apply(audio_segment: AudioSegment) -> AudioSegment:
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    sample_rate = audio_segment.frame_rate

    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).T
    else:
        samples = samples.reshape((1, -1))

    samples /= 32768.0

    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=300.0),
        LowpassFilter(cutoff_frequency_hz=3000.0),
        Distortion(drive_db=4.0),
        Compressor(threshold_db=-10.0, ratio=5.0, attack_ms=2.0, release_ms=80.0),
    ])

    processed = board(samples, sample_rate)
    processed = np.clip(processed * 32768.0, -32768, 32767).astype(np.int16)

    if processed.ndim == 2:
        processed = processed.T.flatten()

    return audio_segment._spawn(processed.tobytes())
