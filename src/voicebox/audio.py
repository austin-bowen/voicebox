from dataclasses import dataclass

import numpy as np


@dataclass
class Audio:
    """
    Represents an audio signal.

    Args:
        signal:
            Audio signal represented as a 1D array of samples,
            each in the range ``[-1, 1]``.
        sample_rate:
            Number of samples per second.
    """

    signal: np.ndarray
    sample_rate: int

    @property
    def len_bytes(self) -> int:
        """Length of audio signal in bytes."""
        return self.signal.nbytes

    @property
    def len_seconds(self) -> float:
        """Length of audio signal in seconds."""
        return len(self) / self.sample_rate

    @property
    def sample_period(self) -> float:
        """Sample period in seconds."""
        return 1. / self.sample_rate

    @sample_period.setter
    def sample_period(self, period: float) -> None:
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
        """
        Raises ``ValueError`` if the audio is invalid.

        For an audio to be valid, it must satisfy the following conditions:

        1. Must have at least one sample.
        2. All samples must be in the range ``[-1, 1]``.
        3. The sample rate must be greater than 0.
        """

        if len(self) and np.any(np.abs(self.signal) > 1.):
            raise ValueError(f'All values in signal must be in range [-1, 1].')

        if self.sample_rate <= 0:
            raise ValueError(f'sample_rate must be > 0; sample_rate={self.sample_rate}')

    def copy(self, signal: np.ndarray = None, sample_rate: int = None) -> 'Audio':
        """Returns a deep copy of self, with optional new property values."""

        return Audio(
            signal=signal if signal is not None else self.signal.copy(),
            sample_rate=sample_rate if sample_rate is not None else self.sample_rate,
        )
