import warnings
from dataclasses import dataclass
from typing import Union, Literal

from voicebox.audio import Audio
from voicebox.sinks.sink import Sink

try:
    import sounddevice as sd
except OSError as e:
    warnings.warn(f'{e.__class__.__name__}: {e}')
    sd = None

Device = Union[int, str]
Latency = Union[float, Literal['low', 'high']]


@dataclass
class SoundDevice(Sink):
    """
    An audio sink that uses the
    `sounddevice <https://python-sounddevice.readthedocs.io/en/0.4.6/>`_
    library to play audio through the default audio device.

    Args:
        device (Device):
            Device index or query string specifying the device to be used.
            If ``None`` (default), a device will be selected automatically.
            See :func:`sounddevice.query_devices()` for valid choices.
        blocking (bool):
            Whether to wait for playback to finish before returning.
        latency (float | 'low' | 'high'):
            The desired latency in seconds. The special values 'low' and 'high'
            select the device's default low and high latency, respectively.
            Lower latency reduces time to playback; higher latency improves
            stability.
    """

    device: Device = None
    blocking: bool = True
    latency: Latency = 0.1

    def play(self, audio: Audio) -> None:
        sd.play(
            audio.signal,
            audio.sample_rate,
            blocking=self.blocking,
            device=self.device,
            latency=self.latency,
        )
