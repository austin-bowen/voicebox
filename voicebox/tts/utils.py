import wave
from pathlib import Path

import numpy as np

from voicebox.audio import Audio


def get_audio_from_wav_file(file_path: Path) -> Audio:
    with wave.open(str(file_path), 'rb') as wav_file:
        bits_per_sample = 8 * wav_file.getsampwidth()
        signal_bytes = wav_file.readframes(-1)
        sample_rate = wav_file.getframerate()

    dtype = {
        8: np.uint8,
        16: np.int16,
        32: np.int32,
    }[bits_per_sample]
    signal = np.frombuffer(signal_bytes, dtype=dtype)

    # Scale to [-1, 1]
    max_value = 2 ** (bits_per_sample - 1)
    signal = signal.astype(float) / max_value

    return Audio(signal, sample_rate)
