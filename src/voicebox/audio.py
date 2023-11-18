from dataclasses import dataclass

import numpy as np


@dataclass
class Audio:
    signal: np.ndarray
    """Audio signal represented as a 1D array of samples, each in the range [-1, 1]."""

    sample_rate: int
    """Number of samples per second."""

    @property
    def len_bytes(self) -> int:
        """Length of audio signal in bytes."""
        return self.signal.nbytes

    @property
    def len_seconds(self) -> float:
        """Length of audio signal in seconds."""
        return len(self) / self.sample_rate

    @property
    def period(self) -> float:
        return 1. / self.sample_rate

    @period.setter
    def period(self, period: float) -> None:
        self.sample_rate = round(1. / period)

    def __eq__(self, other: 'Audio') -> bool:
        return (
            other.signal.shape == self.signal.shape
            and np.allclose(self.signal, other.signal)
            and self.sample_rate == other.sample_rate
        )

    def __len__(self) -> int:
        """Number of samples in audio signal."""
        return len(self.signal)

    def check(self) -> None:
        """Raises ValueError if the audio is invalid."""

        if len(self) and np.any(np.abs(self.signal) > 1.):
            raise ValueError(f'All values in signal must be in range [-1, 1].')

        if self.sample_rate <= 0:
            raise ValueError(f'sample_rate must be > 0; sample_rate={self.sample_rate}')

    def copy(self, signal: np.ndarray = None, sample_rate: int = None) -> 'Audio':
        return Audio(
            signal=signal if signal is not None else self.signal.copy(),
            sample_rate=sample_rate if sample_rate is not None else self.sample_rate,
        )
