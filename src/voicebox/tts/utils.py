import wave
from pathlib import Path
from typing import TypeVar, Iterable, Optional, Tuple

import audioread
import numpy as np

from voicebox.audio import Audio
from voicebox.types import FileOrPath

K = TypeVar('K')
V = TypeVar('V')

dtype_to_sample_width = {
    np.dtype('int8'): 1,
    np.dtype('int16'): 2,
    np.dtype('int32'): 4,
}

sample_width_to_dtype = {
    1: np.int8,
    2: np.int16,
    4: np.int32,
}


def get_audio_from_mp3(file) -> Audio:
    """Returns an :class:`Audio` instance from an MP3 file."""

    with audioread.audio_open(file) as f:
        sample_rate = f.samplerate
        samples = np.frombuffer(b''.join(f.read_data()), dtype=np.int16)

    return get_audio_from_samples(samples, sample_rate)


def get_audio_from_samples(samples: np.ndarray, sample_rate: int) -> Audio:
    """
    Takes raw int-typed samples and a sample rate, and returns an
    :class:`Audio` instance with ``signal`` properly scaled to range
    ``[-1, 1)``.

    Args:
        samples:
            The raw samples as a numpy array.
            dtype must be int8, int16, or int32.
        sample_rate:
            The sample rate of the samples in Hz.
    """

    bytes_per_sample = dtype_to_sample_width[samples.dtype]
    max_value = 2 ** (8 * bytes_per_sample - 1)

    # Scale to [-1, 1)
    signal = samples.astype(float) / max_value
    signal = signal.astype(np.float32)

    return Audio(signal, sample_rate)


def get_audio_from_wav_file(file_or_path: FileOrPath) -> Audio:
    """Returns an :class:`Audio` instance from a WAV file."""

    if isinstance(file_or_path, Path):
        file_or_path = str(file_or_path)

    with wave.open(file_or_path, 'rb') as wav_file:
        bytes_per_sample = wav_file.getsampwidth()
        sample_bytes = wav_file.readframes(-1)
        sample_rate = wav_file.getframerate()

    dtype = sample_width_to_dtype[bytes_per_sample]
    samples = np.frombuffer(sample_bytes, dtype=dtype)

    return get_audio_from_samples(samples, sample_rate)


def add_optional_items(d: dict, items: Iterable[Tuple[K, Optional[V]]]) -> dict:
    """Adds items with non-null values to the given dict."""

    for k, v in items:
        if v is not None:
            d[k] = v

    return d
