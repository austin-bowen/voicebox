import wave
from pathlib import Path
from typing import TypeVar, Iterable, Optional, Tuple

import numpy as np

from voicebox.audio import Audio
from voicebox.types import FileOrPath

try:
    import pydub
    from pydub import AudioSegment
except ImportError:
    pydub = None

K = TypeVar('K')
V = TypeVar('V')

if pydub:
    def get_audio_from_audio_segment(audio_segment: AudioSegment) -> Audio:
        bits_per_sample = 8 * audio_segment.frame_width
        max_value = 2 ** (bits_per_sample - 1)

        signal = np.array(audio_segment.get_array_of_samples(), dtype=float)
        signal /= max_value
        signal = signal.astype(np.float32)

        return Audio(signal, sample_rate=audio_segment.frame_rate)


    def get_audio_from_mp3(file) -> Audio:
        return get_audio_from_audio_segment(AudioSegment.from_mp3(file))


def get_audio_from_wav_file(file_or_path: FileOrPath) -> Audio:
    if isinstance(file_or_path, Path):
        file_or_path = str(file_or_path)

    with wave.open(file_or_path, 'rb') as wav_file:
        bytes_per_sample = wav_file.getsampwidth()
        signal_bytes = wav_file.readframes(-1)
        sample_rate = wav_file.getframerate()

    try:
        dtype = {
            1: np.int8,
            2: np.int16,
            4: np.int32,
        }[bytes_per_sample]
    except KeyError:
        raise ValueError(f'Unsupported sample width: {bytes_per_sample}')

    signal = np.frombuffer(signal_bytes, dtype=dtype)

    # Scale to [-1, 1)
    max_value = 2 ** (8 * bytes_per_sample - 1)
    signal = signal.astype(float) / max_value
    signal = signal.astype(np.float32)

    return Audio(signal, sample_rate)


def add_optional_items(d: dict, items: Iterable[Tuple[K, Optional[V]]]) -> None:
    for k, v in items:
        if v is not None:
            d[k] = v
