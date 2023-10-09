from dataclasses import dataclass

import numpy as np


@dataclass
class Audio:
    signal: np.ndarray
    sample_rate: int

    @property
    def period(self) -> float:
        return 1. / self.sample_rate

    @period.setter
    def period(self, period: float) -> None:
        self.sample_rate = round(1. / period)

    def __eq__(self, other: 'Audio') -> bool:
        return np.allclose(self.signal, other.signal) and self.sample_rate == other.sample_rate

    def copy(self, signal: np.ndarray = None, sample_rate: int = None) -> 'Audio':
        return Audio(
            signal=signal if signal is not None else self.signal.copy(),
            sample_rate=sample_rate if sample_rate is not None else self.sample_rate,
        )
