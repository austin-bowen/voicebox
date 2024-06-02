__all__ = ['RingMod']

from math import pi
from typing import Callable

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import EffectWithDryWet

WaveFunc = Callable[[np.ndarray], np.ndarray]


class RingMod(EffectWithDryWet):
    """
    Ring modulation effect.

    Multiplies the audio signal by a carrier wave.
    Can be used to create choppy, Doctor Who Dalek-like effects
    at low carrier frequencies, or bell-like sounds at higher
    carrier frequencies.

    Args:
        carrier_freq (float):
            Carrier wave frequency in Hz.
        carrier_wave:
            Carrier wave function. Defaults to ``np.sin``.
        dry:
            Dry (input) signal level. 0 is none, 1 is unity. Default is .5.
        wet:
            Wet (affected) signal level. 0 is none, 1 is unity. Default is .5.
    """

    carrier_freq: float = 20.
    carrier_wave: WaveFunc = np.sin

    def __init__(
            self,
            carrier_freq: float = 20.,
            carrier_wave: WaveFunc = np.sin,
            dry: float = 0.5,
            wet: float = 0.5,
    ):
        super().__init__(dry, wet)

        self.carrier_freq = carrier_freq
        self.carrier_wave = carrier_wave

    def get_wet_signal(self, audio: Audio) -> np.ndarray:
        t = np.arange(len(audio.signal)) / audio.sample_rate
        carrier_signal = self.carrier_wave(2 * pi * self.carrier_freq * t)
        return audio.signal * carrier_signal
