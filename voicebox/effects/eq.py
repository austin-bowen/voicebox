from abc import abstractmethod
from dataclasses import dataclass
from typing import Union, Tuple, Literal

from scipy.signal import lfilter, butter

from voicebox.audio import Audio
from voicebox.effects.effect import Effect
from voicebox.effects.utils import CallCache

__all__ = [
    'ButterworthFilter',
    'BandPassFilter',
    'BandStopFilter',
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


@dataclass
class ButterworthFilter(Filter):
    """Butterworth filter."""

    btype: Literal['lowpass', 'highpass', 'bandpass', 'bandstop']
    freq: Union[float, Tuple[float, float]]
    order: int

    def __init__(self, btype, freq, order: int = 1):
        self.btype = btype
        self.freq = freq
        self.order = order

        self._build_filter_params = CallCache(self._build_filter_params)

    def _get_filter_params(self, audio: Audio):
        return self._build_filter_params(
            audio.sample_rate,
            self.freq,
            self.order,
            self.btype,
        )

    @staticmethod
    def _build_filter_params(sample_rate, freq, order, btype):
        freq = ButterworthFilter._convert_freq(sample_rate, freq)
        return butter(order, freq, btype=btype)

    @staticmethod
    def _convert_freq(sample_rate, freq):
        nyquist = .5 * sample_rate

        if isinstance(freq, (int, float)):
            return freq / nyquist
        else:
            low, high = freq
            return low / nyquist, high / nyquist


class BandFilterMixin:
    freq: Tuple[float, float]

    @property
    def low_freq(self) -> float:
        return self.freq[0]

    @low_freq.setter
    def low_freq(self, low_freq) -> None:
        self.freq = (low_freq, self.high_freq)

    @property
    def high_freq(self) -> float:
        return self.freq[1]

    @high_freq.setter
    def high_freq(self, high_freq: float) -> None:
        self.freq = (self.low_freq, high_freq)

    @property
    def center_freq(self) -> float:
        return sum(self.freq) / 2

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


class BandPassFilter(ButterworthFilter, BandFilterMixin):
    """Band-pass Butterworth filter."""

    def __init__(self, low_freq: float, high_freq: float, order: int = 1):
        super().__init__('bandpass', (low_freq, high_freq), order=order)

    @staticmethod
    def from_center(center_freq: float, bandwidth: float, order: int = 1) -> 'BandPassFilter':
        bandwidth /= 2
        return BandPassFilter(
            low_freq=center_freq - bandwidth,
            high_freq=center_freq + bandwidth,
            order=order,
        )


class BandStopFilter(ButterworthFilter, BandFilterMixin):
    """Band-stop Butterworth filter."""

    def __init__(self, low_freq: float, high_freq: float, order: int = 1):
        super().__init__('bandstop', (low_freq, high_freq), order=order)

    @staticmethod
    def from_center(center_freq: float, bandwidth: float, order: int = 1) -> 'BandStopFilter':
        bandwidth /= 2
        return BandStopFilter(
            low_freq=center_freq - bandwidth,
            high_freq=center_freq + bandwidth,
            order=order,
        )


class HighPassFilter(ButterworthFilter):
    """High-pass Butterworth filter."""

    def __init__(self, freq: float, order: int = 1):
        super().__init__('highpass', freq, order=order)


class LowPassFilter(ButterworthFilter):
    """Low-pass Butterworth filter."""

    def __init__(self, freq: float, order: int = 1):
        super().__init__('lowpass', freq, order=order)
