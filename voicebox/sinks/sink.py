from abc import ABC, abstractmethod

from voicebox.audio import Audio


class Sink(ABC):
    @abstractmethod
    def play(self, audio: Audio) -> None:
        ...
