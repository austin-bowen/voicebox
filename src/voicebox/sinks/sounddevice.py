from dataclasses import dataclass

import sounddevice as sd

from voicebox.sinks.sink import Sink
from voicebox.audio import Audio


@dataclass
class SoundDevice(Sink):
    """An audio sink based on the [sounddevice](https://python-sounddevice.readthedocs.io/en/0.4.6/) library."""

    blocking: bool = True
    """Whether to wait for playback to finish before returning."""

    def play(self, audio: Audio) -> None:
        sd.play(audio.signal, audio.sample_rate, blocking=self.blocking)
