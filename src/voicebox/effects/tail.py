__all__ = ['Tail']

from dataclasses import dataclass

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect


@dataclass
class Tail(Effect):
    """
    Adds ``seconds`` of silence to the end of the audio.

    This is useful for adding space between audio clips,
    or for allowing time-based effects (e.g. reverb) to
    decay naturally instead of being abruptly cut off.
    """

    seconds: float = 1.

    def apply(self, audio: Audio) -> Audio:
        samples = round(self.seconds * audio.sample_rate)
        tail = np.zeros(samples, dtype=audio.signal.dtype)
        audio.signal = np.concatenate([audio.signal, tail])
        return audio
