from dataclasses import dataclass, field
from random import Random
from typing import Callable, Sequence

import numpy as np
from scipy.signal import butter, lfilter

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['Vocoder']


def sawtooth_wave(radians: np.ndarray) -> np.ndarray:
    out = (radians % (2 * np.pi)) / (2 * np.pi)
    out = 2 * out - 1
    return out


@dataclass
class SawtoothWave:
    freq: float

    def __call__(self, times: np.ndarray) -> np.ndarray:
        radians = 2 * np.pi * self.freq * times
        return sawtooth_wave(radians)


@dataclass
class RandomSawtoothWave:
    min_freq: float
    max_freq: float
    pitch_duration: float

    rng: Random = field(default_factory=Random)

    def __call__(self, times: np.ndarray) -> np.ndarray:
        dt = times[1] - times[0]
        chunk_size = round(self.pitch_duration / dt)

        alpha = np.log2(self.max_freq / self.min_freq)

        out = np.zeros_like(times)
        for i in range(0, len(times), chunk_size):
            f = self.min_freq * 2 ** (alpha * self.rng.random())
            time_chunk = times[i:i + chunk_size]
            radians = 2 * np.pi * f * time_chunk
            out[i:i + chunk_size] = sawtooth_wave(radians)

        return out


class EnvelopeFollower(Effect):
    """
    Basic envelope follower that rectifies the input signal and applies a Butterworth LPF.
    """

    freq: float
    order: int

    def __init__(self, freq: float = 50, order: int = 1):
        self.freq = freq
        self.order = order

        self._prev_filter_args = None
        self._lpf_params = None

    def apply(self, audio: Audio) -> Audio:
        lpf_params = self._get_lpf_params(audio)
        new_signal = np.abs(audio.signal)
        new_signal = lfilter(*lpf_params, new_signal)
        return audio.copy(signal=new_signal)

    def _get_lpf_params(self, audio: Audio):
        nyquist = .5 * audio.sample_rate
        f = self.freq / nyquist
        filter_args = (self.order, f)

        if filter_args != self._prev_filter_args:
            self._lpf_params = butter(*filter_args, btype='low', analog=False, output='ba')

        return self._lpf_params


class BandpassFilter(Effect):
    center_freq: float
    bandwidth: float
    order: int

    def __init__(self, center_freq: float, bandwidth: float, order: int = 1):
        self.center_freq = center_freq
        self.bandwidth = bandwidth
        self.order = order

        self._prev_filter_args = None
        self._filter_params = None

    @property
    def low_freq(self) -> float:
        return self.center_freq - self.bandwidth / 2

    @property
    def high_freq(self) -> float:
        return self.center_freq + self.bandwidth / 2

    def apply(self, audio: Audio) -> Audio:
        filter_params = self._get_filter_params(audio)
        new_signal = lfilter(*filter_params, audio.signal)
        return audio.copy(signal=new_signal)

    def _get_filter_params(self, audio: Audio):
        nyquist = .5 * audio.sample_rate
        low_freq = self.low_freq / nyquist
        high_freq = self.high_freq / nyquist
        filter_args = (self.order, (low_freq, high_freq))

        if filter_args != self._prev_filter_args:
            self._filter_params = butter(*filter_args, btype='band', analog=False, output='ba')

        return self._filter_params


@dataclass
class Vocoder(Effect):
    carrier_wave: Callable[[np.ndarray], np.ndarray]
    """Takes in an array of sample times and outputs corresponding wave samples."""

    bandpass_filters: Sequence[BandpassFilter]

    envelope_follower: EnvelopeFollower

    @staticmethod
    def build(
            carrier_freq: float = 150.,
            carrier_wave_builder=SawtoothWave,
            min_freq: float = 100.,
            max_freq: float = 10_000.,
            bands: int = 40,
            bandwidth: float = 0.5,
            bandpass_filter_builder=BandpassFilter,
            bandpass_filter_order: int = 3,
            envelope_follower_freq: float = 50.,
            envelope_follower_builder=EnvelopeFollower,
    ) -> 'Vocoder':
        carrier_wave = carrier_wave_builder(carrier_freq)

        bandpass_filters = []
        alpha = np.log2(max_freq / min_freq)
        for band in range(bands):
            f = min_freq * 2 ** (alpha * band / (bands - 1))
            f_next = min_freq * 2 ** (alpha * (band + 1) / (bands - 1))
            width = bandwidth * (f_next - f)

            bandpass_filters.append(
                bandpass_filter_builder(f, width, bandpass_filter_order)
            )

        envelope_follower = envelope_follower_builder(envelope_follower_freq)

        return Vocoder(carrier_wave, bandpass_filters, envelope_follower)

    def apply(self, audio: Audio) -> Audio:
        carrier = self._get_carrier(audio)

        new_signals = [
            self._get_carrier_signal_for_band(audio, carrier, bpf)
            for bpf in self.bandpass_filters
        ]

        audio.signal = np.sum(new_signals, axis=0)

        return audio

    def _get_carrier(self, audio: Audio) -> Audio:
        t = np.arange(len(audio)) * audio.period
        carrier = self.carrier_wave(t)
        return audio.copy(signal=carrier)

    def _get_carrier_signal_for_band(self, modulator: Audio, carrier: Audio, bpf: BandpassFilter) -> np.ndarray:
        filtered_modulator = bpf(modulator.copy())
        modulator_level = self.envelope_follower(filtered_modulator).signal

        carrier_signal = bpf(carrier.copy()).signal
        carrier_signal *= modulator_level

        return carrier_signal
