from dataclasses import dataclass

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['Delay']


@dataclass
class Delay(Effect):
    time: float = 0.1
    repeats: int = 1
    dry: float = 1.
    wet: float = 1.
    decay: float = 1.
    trail: bool = True

    def apply(self, audio: Audio) -> Audio:
        offset = self._get_offset(audio)

        original_signal = audio.signal.copy()
        audio.signal *= self.dry

        if self.trail:
            additional_samples = np.zeros(offset * self.repeats)
            audio.signal = np.concatenate([audio.signal, additional_samples])

        for repeat in range(1, self.repeats + 1):
            start = repeat * offset
            end = start + len(original_signal)
            gain = self.wet * self.decay ** (repeat - 1)
            audio.signal[start:end] += gain * original_signal

        return audio

    def _get_offset(self, audio: Audio) -> int:
        return round(self.time * audio.sample_rate)
