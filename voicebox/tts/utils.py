import wave
from pathlib import Path

import numpy as np

from voicebox.types import Audio


PCM_16_BIT_MAX_VALUE = 2 ** 15 - 1


def get_audio_from_wav_file(file_path: Path) -> Audio:
    with wave.open(str(file_path), 'rb') as wav_file:
        signal_bytes = wav_file.readframes(-1)
        sample_rate = wav_file.getframerate()

    # Assuming 16-bit PCM
    signal = np.frombuffer(signal_bytes, dtype=np.int16)
    signal = signal.astype(float) / PCM_16_BIT_MAX_VALUE

    return Audio(signal, sample_rate)
