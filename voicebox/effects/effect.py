from abc import ABC, abstractmethod

from voicebox.audio import Audio


class Effect(ABC):
    def __call__(self, audio: Audio) -> Audio:
        return self.apply(audio)

    @abstractmethod
    def apply(self, audio: Audio) -> Audio:
        ...
