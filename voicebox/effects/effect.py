from abc import ABC, abstractmethod
from typing import Sequence, Callable

import numpy as np

from voicebox.audio import Audio


class Effect(ABC):
    def __call__(self, audio: Audio) -> Audio:
        return self.apply(audio)

    @abstractmethod
    def apply(self, audio: Audio) -> Audio:
        ...


class SeriesChain(Effect):
    """Applies a chain of effects serially."""

    effects: Sequence[Effect]

    def __init__(self, *effects: Effect):
        self.effects = effects

    def apply(self, audio: Audio) -> Audio:
        for effect in self.effects:
            audio = effect(audio)

        return audio


class ParallelChain(Effect):
    """
    Applies effects in parallel and combines the outputs.

    All effects must output audios with the same sample rate.
    The combined output audio will expand to fit the longest effect audio.
    """

    effects: Sequence[Effect]
    dry_gain: float
    combine_func: Callable[[np.ndarray], np.ndarray]

    def __init__(
            self,
            *effects: Effect,
            dry_gain: float = 0.,
            combine_func: Callable[..., np.ndarray] = np.sum,
    ):
        self.effects = effects
        self.dry_gain = dry_gain
        self.combine_func = combine_func

    def apply(self, audio: Audio) -> Audio:
        audios = []

        if self.dry_gain > 0:
            dry_audio = audio.copy()
            dry_audio.signal *= self.dry_gain
            audios.append(dry_audio)

        for effect in self.effects:
            audios.append(effect(audio.copy()))

        sample_rates = set(a.sample_rate for a in audios)
        if len(sample_rates) != 1:
            raise RuntimeError(f'All sample rates must be the same; got sample rates: {sample_rates}')
        sample_rate = tuple(sample_rates)[0]

        max_length = max(len(a) for a in audios)
        signals = np.zeros((len(audios), max_length))
        for i, a in enumerate(audios):
            signals[i, :len(a)] = a.signal

        signal = self.combine_func(signals, axis=0)
        assert len(signal) == max_length

        return Audio(signal, sample_rate)
