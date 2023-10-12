from dataclasses import dataclass

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['Normalize']


@dataclass
class Normalize(Effect):
    """Normalizes audio such that max(abs(signal)) == `max_amplitude` (1.0 by default)."""

    max_amplitude: float = 1.0

    def apply(self, audio: Audio) -> Audio:
        max_value = np.abs(audio.signal).max()

        if max_value > 0:
            audio.signal *= self.max_amplitude / max_value

        return audio
