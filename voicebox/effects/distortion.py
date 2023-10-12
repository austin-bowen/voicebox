from dataclasses import dataclass

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['Bitcrusher', 'ClipDistortion', 'TanhDistortion']


@dataclass
class Bitcrusher(Effect):
    bits: int = 4

    def apply(self, audio: Audio) -> Audio:
        min_sample = np.min(audio.signal)
        max_sample = np.max(audio.signal)

        # Scale to [0, 1]
        signal = (audio.signal - min_sample) / (max_sample - min_sample)

        values = 2 ** self.bits - 1
        signal = np.round(values * signal) / values

        audio.signal = signal * (max_sample - min_sample) + min_sample

        return audio


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
