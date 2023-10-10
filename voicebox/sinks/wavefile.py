import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from voicebox.audio import Audio
from voicebox.sinks.sink import Sink
from voicebox.types import FileOrPath


@dataclass
class WaveFile(Sink):
    file: FileOrPath
    sample_width: int = 2

    def play(self, audio: Audio) -> None:
        write_audio_to_wave(audio, self.file, sample_width=self.sample_width)


def write_audio_to_wave(audio, file_or_path: FileOrPath, sample_width: int = 2) -> None:
    if isinstance(file_or_path, Path):
        file_or_path = str(file_or_path)

    bits_per_sample = 8 * sample_width
    dtype = {
        8: np.uint8,
        16: np.int16,
        32: np.int32,
    }[bits_per_sample]

    # Assuming signal is in range[-1, 1], scale to [-max_value, max_value]
    max_value = 2 ** (bits_per_sample - 1) - 1
    signal = np.round(audio.signal * max_value).astype(dtype)
    signal_bytes = signal.tobytes()

    with wave.open(file_or_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(audio.sample_rate)
        wav_file.writeframes(signal_bytes)
