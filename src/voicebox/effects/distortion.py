from dataclasses import dataclass

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['ClipDistortion', 'TanhDistortion']


@dataclass
class ClipDistortion(Effect):
    gain: float = 1.
    max_value: float = 1.

    def apply(self, audio: Audio) -> Audio:
        audio.signal = np.clip(self.gain * audio.signal, -self.max_value, self.max_value)
        return audio


@dataclass
class TanhDistortion(Effect):
    gain: float = 1.

    def apply(self, audio: Audio) -> Audio:
        audio.signal = np.tanh(self.gain * audio.signal)
        return audio
