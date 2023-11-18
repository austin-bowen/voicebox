import os
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from voicebox.audio import Audio
from voicebox.sinks.sink import Sink
from voicebox.tts.utils import get_audio_from_wav_file, sample_width_to_dtype
from voicebox.types import FileOrPath


@dataclass
class WaveFile(Sink):
    file: FileOrPath
    append: bool = False
    sample_width: int = 2

    def play(self, audio: Audio) -> None:
        write_audio_to_wav(audio, self.file, append=self.append, sample_width=self.sample_width)


def write_audio_to_wav(
        audio: Audio,
        file_or_path: FileOrPath,
        append: bool = False,
        sample_width: int = 2,
) -> None:
    audio.check()

    if isinstance(file_or_path, (Path, str)):
        file_or_path = str(file_or_path)
        needs_append = append and os.path.isfile(file_or_path)
    else:
        # file_or_path is file-like object
        needs_append = False

    if needs_append:
        existing_audio = get_audio_from_wav_file(file_or_path)

        if audio.sample_rate != existing_audio.sample_rate:
            raise ValueError(
                f'Cannot append audio to existing file {file_or_path}: '
                f'Sample rates do not match: '
                f'new={audio.sample_rate}; '
                f'existing={existing_audio.sample_rate}'
            )

        signal = np.concatenate([existing_audio.signal, audio.signal])
    else:
        signal = audio.signal

    dtype = sample_width_to_dtype[sample_width]

    # Assuming signal is in range[-1, 1], scale to [-max_value, max_value)
    max_value = 2 ** (8 * sample_width - 1)
    signal = np.round(signal * max_value)
    signal = signal.clip(max=max_value - 1)
    signal = signal.astype(dtype)
    signal_bytes = signal.tobytes()

    with wave.open(file_or_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(audio.sample_rate)
        wav_file.writeframes(signal_bytes)
