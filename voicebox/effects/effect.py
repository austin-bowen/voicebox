from abc import ABC, abstractmethod

from voicebox.audio import Audio


class Effect(ABC):
    @abstractmethod
    def apply(self, audio: Audio) -> Audio:
        ...
