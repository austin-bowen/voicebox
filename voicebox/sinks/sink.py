from abc import ABC, abstractmethod

from voicebox.audio import Audio


class Sink(ABC):
    def __call__(self, audio: Audio) -> None:
        return self.play(audio)

    @abstractmethod
    def play(self, audio: Audio) -> None:
        ...
