from dataclasses import dataclass
from typing import Sequence

from voicebox.sinks.sink import Sink


@dataclass
class Distributor(Sink):
    """Distributes audio to multiple sinks."""

    sinks: Sequence[Sink]

    def play(self, audio):
        for sink in self.sinks:
            sink.play(audio)
