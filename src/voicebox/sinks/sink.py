from abc import ABC, abstractmethod

from voicebox.audio import Audio


class Sink(ABC):
    """Base class for audio sinks."""

    def __call__(self, audio: Audio) -> None:
        return self.play(audio)

    @abstractmethod
    def play(self, audio: Audio) -> None:
        ...  # pragma: no cover
