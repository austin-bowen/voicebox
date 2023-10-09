from dataclasses import dataclass

import numpy as np


@dataclass
class Audio:
    signal: np.ndarray
    sample_rate: int

    def __eq__(self, other: 'Audio') -> bool:
        return np.allclose(self.signal, other.signal) and self.sample_rate == other.sample_rate

    def copy(self, signal: np.ndarray = None, sample_rate: int = None) -> 'Audio':
        return Audio(
            signal=signal if signal is not None else self.signal.copy(),
            sample_rate=sample_rate if sample_rate is not None else self.sample_rate,
        )
