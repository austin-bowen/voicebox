from voicebox.sinks.distributor import Distributor
from voicebox.sinks.sink import Sink
from voicebox.sinks.sounddevice import SoundDevice
from voicebox.sinks.wavefile import WaveFile


def default_sink() -> Sink:
    """Returns a new instance of the default sink, ``SoundDevice``."""
    return SoundDevice()
