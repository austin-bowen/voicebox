from abc import ABC, abstractmethod

from voicebox.types import Audio


class Sink(ABC):
    @abstractmethod
    def play(self, audio: Audio) -> None:
        ...
