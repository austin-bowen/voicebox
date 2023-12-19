"""
Equalization effects module.

See ``Filter.build()`` for building basic filter effects.

Simple example:
    >>> from voicebox.effects import Filter
    >>> filter = Filter.build('highpass', 200)
    >>> filter = Filter.build('bandpass', (100, 10000))
"""

from abc import abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import Union, Tuple, Literal, Optional

import numpy as np
from scipy.signal import sosfilt, iirfilter

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = [
    'center_to_band',
    'Filter',
    'FilterParamBuilder',
    'IIRFilterParamBuilder',
]

BType = Literal['lowpass', 'highpass', 'bandpass', 'bandstop']
FType = Literal['butter', 'cheby1', 'cheby2', 'ellip', 'bessel']
Freq = Union[int, float]
Band = Tuple[Freq, Freq]
FreqOrBand = Union[Freq, Band]
SosFilterParam = np.ndarray

# Cache filter parameter building function
iirfilter = lru_cache(iirfilter)


def center_to_band(freq: Freq, bandwidth: Freq) -> Band:
    """Converts a center frequency with bandwidth to a frequency band."""
    bandwidth /= 2
    return freq - bandwidth, freq + bandwidth


class FilterParamBuilder:
    @abstractmethod
    def build(self, sample_rate: float) -> SosFilterParam:
        """Returns filter parameters in ``sos`` format."""


@dataclass
class IIRFilterParamBuilder(FilterParamBuilder):
    order: int
    freq: FreqOrBand
    rp: Optional[float]
    rs: Optional[float]
    btype: BType
    ftype: FType

    def build(self, sample_rate: float) -> SosFilterParam:
        return iirfilter(
            self.order,
            self.freq,
            rp=self.rp,
            rs=self.rs,
            btype=self.btype,
            analog=False,
            ftype=self.ftype,
            output='sos',
            fs=sample_rate,
        )


@dataclass
class Filter(Effect):
    filter_param_builder: FilterParamBuilder

    @classmethod
    def build(
            cls,
            btype: BType,
            freq: FreqOrBand,
            order: int = 1,
            rp: float = None,
            rs: float = None,
            ftype: FType = 'butter',
    ) -> 'Filter':
        """
        Builds a filter using ``scipy.signal.iirfilter``.

        See here for details:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.iirfilter.html

        Args:
            btype (BType):
                The type of filter. Should be one of ``'lowpass'``,
                ``'highpass'``, ``'bandpass'``, or ``'bandstop'``.
            freq (FreqOrBand):
                The filter frequency in Hz. Should be a single number for lowpass/highpass,
                or a frequency band as a sequence ``(low_freq, high_freq)`` for bandpass/bandstop.
                See the ``center_to_band()`` function for easy converting from a center freq with
                bandwidth to a frequency band.
            order (int, optional):
                The order of the filter. Defaults to 1.
                Higher orders will have faster dropoffs.
            rp (float, optional):
                For Chebyshev and elliptic filters, provides the maximum
                ripple in the passband. (dB)
            rs (float, optional):
                For Chebyshev and elliptic filters, provides the minimum
                attenuation in the stop band. (dB)
            ftype (FType, optional):
                The type of IIR filter to design. Defaults to ``'butter'``.
                Should be one of:

                - ``'butter'`` (Butterworth)
                - ``'cheby1'`` (Chebychev I)
                - ``'cheby2'`` (Chebychev II)
                - ``'ellip'`` (Cauer/elliptic)
                - ``'bessel'`` (Bessel/Thomson)

        Returns:
            Filter: A Filter instance with the specified parameters.
        """

        param_builder = IIRFilterParamBuilder(order, freq, rp, rs, btype, ftype)
        return cls(param_builder)

    def apply(self, audio: Audio) -> Audio:
        filter_params = self.filter_param_builder.build(audio.sample_rate)
        new_signal = sosfilt(filter_params, audio.signal)
        return audio.copy(signal=new_signal)
