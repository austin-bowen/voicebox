from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np

from voicebox.audio import Audio
from voicebox.sinks import SoundDevice, WaveFile


def build_audio(duration_s: float = 0.5) -> Audio:
    sample_rate = 44100

    samples = int(duration_s * sample_rate)

    signal = 2 * np.random.rand(samples) - 1
    signal *= 0.01

    return Audio(signal, sample_rate)


def test_sound_device_sink() -> None:
    audio = build_audio()
    sink = SoundDevice()
    sink.play(audio)


def test_wave_file_sink() -> None:
    audio = build_audio()

    with NamedTemporaryFile() as file:
        file.close()
        file_path = Path(file.name)

        sink = WaveFile(file_path)
        sink.play(audio)

        file_size = file_path.stat().st_size
        assert file_size > 0
