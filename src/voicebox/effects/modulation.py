from dataclasses import dataclass
from math import pi
from typing import Callable

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['RingMod']


@dataclass
class RingMod(Effect):
    carrier_freq: float = 20.
    blend: float = 0.5
    carrier_wave: Callable[[np.ndarray], np.ndarray] = np.sin

    def apply(self, audio: Audio) -> Audio:
        t = np.arange(len(audio.signal)) / audio.sample_rate
        carrier_signal = self.carrier_wave(2 * pi * self.carrier_freq * t)
        mod_signal = audio.signal * carrier_signal
        audio.signal = (1 - self.blend) * audio.signal + self.blend * mod_signal
        return audio
