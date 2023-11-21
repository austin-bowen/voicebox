from dataclasses import dataclass
from typing import Union, Literal

import sounddevice as sd

from voicebox.sinks.sink import Sink
from voicebox.audio import Audio


Device = Union[int, str]
Latency = Union[float, Literal['low', 'high']]


@dataclass
class SoundDevice(Sink):
    """An audio sink based on the [sounddevice](https://python-sounddevice.readthedocs.io/en/0.4.6/) library."""

    device: Device = None
    """
    Device index or query string specifying the device to be used.
    If ``None`` (default), a device will be selected automatically.
    See function ``sounddevice.query_devices()`` for valid choices.
    """

    blocking: bool = True
    """Whether to wait for playback to finish before returning."""

    latency: Latency = 0.1
    """
    The desired latency in seconds. The special values 'low' and 'high'
    select the device's default low and high latency, respectively.
    Lower latency reduces time to playback; higher latency improves stability.
    """

    def play(self, audio: Audio) -> None:
        sd.play(
            audio.signal,
            audio.sample_rate,
            blocking=self.blocking,
            device=self.device,
            latency=self.latency,
        )
