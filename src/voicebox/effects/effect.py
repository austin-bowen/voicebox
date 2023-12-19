__all__ = ["Effect", "Effects"]

from abc import ABC, abstractmethod
from typing import List

from voicebox.audio import Audio


class Effect(ABC):
    """Base class for all effects."""

    def __call__(self, audio: Audio) -> Audio:
        return self.apply(audio)

    @abstractmethod
    def apply(self, audio: Audio) -> Audio:
        """
        Applies the effect to the audio signal.

        May or may not return a new ``Audio`` instance.
        """

        ...


Effects = List[Effect]
