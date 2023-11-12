import time
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['Flanger']


@dataclass
class Flanger(Effect):
    rate: float = .15
    """LFO rate in Hz."""

    min_delay: float = .0025
    """Minimum delay time in seconds."""

    max_delay: float = .0035
    """Maximum delay time in seconds."""

    feedback: float = .9
    """Delay feedback. Should be in range (0, 1)."""

    dry: float = .5
    """Dry (input) signal level. 0 is none, 1 is unity."""

    wet: float = 1.
    """Wet (affected) signal level. 0 is none, 1 is unity."""

    t_offset: float = 0.
    """Offset time to add to the LFO time, in seconds."""

    t_offset_func: Optional[Callable[[], float]] = time.monotonic
    """
    Optional function that returns a time by which to offset the LFO time
    (in addition to ``t_offset``). Defaults to a function that returns the
    current time, which makes the LFO phase consistent over time between runs.
    """

    def apply(self, audio: Audio) -> Audio:
        wet_signal = self._get_wet_signal(audio)
        out = self.dry * audio.signal + self.wet * wet_signal
        return audio.copy(signal=out)

    def _get_wet_signal(self, audio: Audio) -> np.ndarray:
        delay_offsets = self._get_delay_offsets(audio)

        wet = np.zeros_like(audio.signal)
        for i, (in_sample, delay_offset) in enumerate(zip(audio.signal, delay_offsets)):
            i_delay = i - delay_offset
            delay_sample = wet[i_delay] if i_delay >= 0 else 0
            wet[i] = in_sample + self.feedback * delay_sample

        return wet

    def _get_delay_offsets(self, audio: Audio) -> np.ndarray:
        t = self._get_time_from_lfo(audio)

        delay_times = np.cos(2 * np.pi * self.rate * t)
        delay_times = (delay_times + 1) / 2
        delay_times = self.min_delay + (self.max_delay - self.min_delay) * delay_times

        return np.round(delay_times * audio.sample_rate).astype(int)

    def _get_time_from_lfo(self, audio: Audio) -> np.ndarray:
        t = np.arange(len(audio)) * audio.period + self.t_offset

        if self.t_offset_func:
            t += self.t_offset_func() % (1 / self.rate)

        return t
