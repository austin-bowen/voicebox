__all__ = ['RingMod']

from dataclasses import dataclass
from math import pi
from typing import Callable

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

WaveFunc = Callable[[np.ndarray], np.ndarray]


@dataclass
class RingMod(Effect):
    """
    Ring modulation effect.

    Multiplies the audio signal by a carrier wave.
    Can be used to create choppy, Doctor Who Dalek-like effects
    at low carrier frequencies, or bell-like sounds at higher
    carrier frequencies.

    Args:
        carrier_freq (float):
            Carrier wave frequency in Hz.
        blend (float):
            Blend between the original and modulated signals.
            0 is all original, 1 is all modulated.
        carrier_wave:
            Carrier wave function. Defaults to ``np.sin``.
    """

    carrier_freq: float = 20.
    blend: float = 0.5
    carrier_wave: WaveFunc = np.sin

    def apply(self, audio: Audio) -> Audio:
        t = np.arange(len(audio.signal)) / audio.sample_rate
        carrier_signal = self.carrier_wave(2 * pi * self.carrier_freq * t)
        mod_signal = audio.signal * carrier_signal
        audio.signal = (1 - self.blend) * audio.signal + self.blend * mod_signal
        return audio
