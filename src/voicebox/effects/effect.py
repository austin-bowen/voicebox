__all__ = [
    'Effect',
    'EffectWithDryWet',
    'Effects',
]

from abc import ABC, abstractmethod
from typing import List

import numpy as np

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

        ...  # pragma: no cover


Effects = List[Effect]


class EffectWithDryWet(Effect, ABC):
    """
    Base class for effects that have a dry/wet mix.

    Args:
        dry:
            Dry (input) signal level. 0 is none, 1 is unity.
        wet:
            Wet (affected) signal level. 0 is none, 1 is unity.
    """

    def __init__(self, dry: float, wet: float):
        self.dry = dry
        self.wet = wet

    def apply(self, audio: Audio) -> Audio:
        dry_signal = audio.signal * self.dry
        wet_signal = self.get_wet_signal(audio) * self.wet
        return audio.copy(signal=dry_signal + wet_signal)

    @abstractmethod
    def get_wet_signal(self, audio: Audio) -> np.ndarray:
        """Returns the "wet" signal (i.e. signal with effect applied)."""
        ...  # pragma: no cover
