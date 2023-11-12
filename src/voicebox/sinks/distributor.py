from dataclasses import dataclass
from typing import Sequence

from voicebox.sinks.sink import Sink


@dataclass
class Distributor(Sink):
    sinks: Sequence[Sink]

    def play(self, audio):
        for sink in self.sinks:
            sink.play(audio)
