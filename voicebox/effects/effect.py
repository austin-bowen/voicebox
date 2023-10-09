from abc import ABC, abstractmethod

from voicebox.types import Audio


class Effect(ABC):
    @abstractmethod
    def apply(self, audio: Audio) -> Audio:
        ...
