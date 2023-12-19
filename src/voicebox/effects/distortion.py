from dataclasses import dataclass

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['TanhDistortion']


@dataclass
class TanhDistortion(Effect):
    gain: float = 1.

    def apply(self, audio: Audio) -> Audio:
        audio.signal = np.tanh(self.gain * audio.signal)
        return audio
