from abc import abstractmethod
from dataclasses import dataclass

from scipy.signal import lfilter, butter

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = [
    'BandPassFilter',
    'HighPassFilter',
    'LowPassFilter',
]


class Filter(Effect):
    def apply(self, audio: Audio) -> Audio:
        filter_params = self._get_filter_params(audio)
        new_signal = lfilter(*filter_params, audio.signal)
        return audio.copy(signal=new_signal)

    @abstractmethod
    def _get_filter_params(self, audio: Audio) -> tuple:
        ...


class BandPassFilter(Filter):
    """Band-pass Butterworth filter."""

    low_freq: float
    high_freq: float
    order: int

    def __init__(self, low_freq: float, high_freq: float, order: int = 1):
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.order = order

        self._prev_filter_args = None
        self._filter_params = None

    @staticmethod
    def from_center(center_freq: float, bandwidth: float, order: int = 1) -> 'BandPassFilter':
        bandwidth /= 2
        return BandPassFilter(
            low_freq=center_freq - bandwidth,
            high_freq=center_freq + bandwidth,
            order=order,
        )

    @property
    def center_freq(self) -> float:
        return self.low_freq + self.bandwidth / 2

    @center_freq.setter
    def center_freq(self, center_freq: float) -> None:
        bandwidth = self.bandwidth / 2
        self.low_freq = center_freq - bandwidth
        self.high_freq = center_freq + bandwidth

    @property
    def bandwidth(self) -> float:
        return self.high_freq - self.low_freq

    @bandwidth.setter
    def bandwidth(self, bandwidth: float) -> None:
        center_freq = self.center_freq
        bandwidth /= 2
        self.low_freq = center_freq - bandwidth
        self.high_freq = center_freq + bandwidth

    def _get_filter_params(self, audio: Audio):
        nyquist = .5 * audio.sample_rate
        low_freq = self.low_freq / nyquist
        high_freq = self.high_freq / nyquist
        filter_args = (self.order, (low_freq, high_freq))

        if filter_args != self._prev_filter_args:
            self._filter_params = butter(*filter_args, btype='band', analog=False, output='ba')

        return self._filter_params


@dataclass
class HighPassFilter(Filter):
    """High-pass Butterworth filter."""

    freq: float
    order: int = 1

    def _get_filter_params(self, audio: Audio) -> tuple:
        nyquist = .5 * audio.sample_rate
        freq = self.freq / nyquist
        return butter(self.order, freq, btype='high', analog=False)


@dataclass
class LowPassFilter(Filter):
    """Low-pass Butterworth filter."""

    freq: float
    order: int = 1

    def _get_filter_params(self, audio: Audio) -> tuple:
        nyquist = .5 * audio.sample_rate
        freq = self.freq / nyquist
        return butter(self.order, freq, btype='low', analog=False)
