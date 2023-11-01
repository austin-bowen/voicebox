from dataclasses import dataclass, field
from random import Random
from typing import Callable, Sequence

import numpy as np
from scipy.signal import butter, lfilter

from voicebox.audio import Audio
from voicebox.effects.effect import Effect
from voicebox.effects.eq import Filter, center_to_band

__all__ = ['Vocoder']

from voicebox.types import KWArgs


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


@dataclass
class Vocoder(Effect):
    carrier_wave: Callable[[np.ndarray], np.ndarray]
    """Takes in an array of sample times and outputs corresponding wave samples."""

    bandpass_filters: Sequence[Filter]

    envelope_follower: EnvelopeFollower

    @staticmethod
    def build(
            carrier_freq: float = 150.,
            carrier_wave_builder=SawtoothWave,
            carrier_wave=None,
            min_freq: float = 100.,
            max_freq: float = 10_000.,
            bands: int = 40,
            bandwidth: float = 0.5,
            bandpass_filter_order: int = 3,
            bandpass_filter_kwargs: KWArgs = None,
            envelope_follower_freq: float = 50.,
            envelope_follower_builder=EnvelopeFollower,
    ) -> 'Vocoder':
        carrier_wave = carrier_wave or carrier_wave_builder(carrier_freq)

        bandpass_filters = []
        alpha = np.log2(max_freq / min_freq)
        for band in range(bands):
            f = min_freq * 2 ** (alpha * band / (bands - 1))
            f_next = min_freq * 2 ** (alpha * (band + 1) / (bands - 1))
            width = bandwidth * (f_next - f)

            bandpass_filters.append(
                Filter.build(
                    'bandpass',
                    freq=center_to_band(f, width),
                    order=bandpass_filter_order,
                    **(bandpass_filter_kwargs or {}),
                )
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

    def _get_carrier_signal_for_band(self, modulator: Audio, carrier: Audio, bpf: Filter) -> np.ndarray:
        filtered_modulator = bpf(modulator.copy())
        modulator_level = self.envelope_follower(filtered_modulator).signal

        carrier_signal = bpf(carrier.copy()).signal
        carrier_signal *= modulator_level

        return carrier_signal
