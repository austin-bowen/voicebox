import sounddevice as sd

from voicebox.sinks.sink import Sink
from voicebox.audio import Audio


class SoundDevice(Sink):
    """An audio sink based on the [sounddevice](https://python-sounddevice.readthedocs.io/en/0.4.6/) library."""

    def play(self, audio: Audio) -> None:
        sd.play(audio.signal, audio.sample_rate)
        sd.wait()
