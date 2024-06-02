__all__ = ['Flanger']

import time
from typing import Callable, Optional

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import EffectWithDryWet


class Flanger(EffectWithDryWet):
    """
    Flanger effect with a very metallic sound.

    Args:
        rate:
            LFO rate in Hz. Default is .15.
        min_delay:
            Minimum delay time in seconds. Default is .0025.
        max_delay:
            Maximum delay time in seconds. Default is .0035.
        feedback:
            Delay feedback. Should be in range (0, 1). Default is .9.
        t_offset:
            Offset time to add to the LFO time, in seconds. Default is 0.
        t_offset_func:
            Optional function that returns a time by which to offset the LFO time
            (in addition to ``t_offset``). Defaults to a function that returns the
            current time, which makes the LFO phase consistent over time between runs.
        dry:
            Dry (input) signal level. 0 is none, 1 is unity. Default is .5.
        wet:
            Wet (affected) signal level. 0 is none, 1 is unity. Default is .5.
    """

    rate: float
    min_delay: float
    max_delay: float
    feedback: float
    t_offset: float
    t_offset_func: Optional[Callable[[], float]]

    def __init__(
            self,
            rate: float = .15,
            min_delay: float = .0025,
            max_delay: float = .0035,
            feedback: float = .9,
            t_offset: float = 0.,
            t_offset_func: Optional[Callable[[], float]] = time.monotonic,
            dry: float = .5,
            wet: float = .5,
    ):
        super().__init__(dry, wet)

        self.rate = rate
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.feedback = feedback
        self.t_offset = t_offset
        self.t_offset_func = t_offset_func

    def get_wet_signal(self, audio: Audio) -> np.ndarray:
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
        t = np.arange(len(audio)) * audio.sample_period + self.t_offset

        if self.t_offset_func:
            t += self.t_offset_func() % (1 / self.rate)

        return t
