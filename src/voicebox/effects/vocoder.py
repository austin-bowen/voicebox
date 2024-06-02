__all__ = ['Vocoder']

import warnings
from dataclasses import dataclass, field
from random import Random
from typing import Callable, Sequence

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect, EffectWithDryWet
from voicebox.effects.eq import Filter, center_to_band
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


@dataclass
class EnvelopeFollower(Effect):
    """
    Basic envelope follower that rectifies the input signal and applies a low-pass filter.
    """

    lpf: Filter

    @classmethod
    def build(
            cls,
            freq: float = 50,
            order: int = 1,
            **filter_kwargs,
    ) -> 'EnvelopeFollower':
        lpf = Filter.build('lowpass', freq, order=order, **filter_kwargs)
        return cls(lpf)

    def apply(self, audio: Audio) -> Audio:
        audio = audio.copy(signal=np.abs(audio.signal))
        audio = self.lpf(audio)
        return audio


class Vocoder(EffectWithDryWet):
    """
    Vocoder effect. Useful for making monotone, robotic voices.

    See ``Vocoder.build()`` to easily construct a Vocoder instance.
    """

    carrier_wave: Callable[[np.ndarray], np.ndarray]
    """Takes in an array of sample times and outputs corresponding wave samples."""

    bandpass_filters: Sequence[Filter]
    envelope_follower: EnvelopeFollower
    max_freq: float

    def __init__(
            self,
            carrier_wave: Callable[[np.ndarray], np.ndarray],
            bandpass_filters: Sequence[Filter],
            envelope_follower: EnvelopeFollower,
            max_freq: float,
            dry: float,
            wet: float,
    ):
        super().__init__(dry, wet)

        self.carrier_wave = carrier_wave
        self.bandpass_filters = bandpass_filters
        self.envelope_follower = envelope_follower
        self.max_freq = max_freq

    @classmethod
    def build(
            cls,
            carrier_freq: float = 160.,
            carrier_wave_builder=SawtoothWave,
            carrier_wave=None,
            min_freq: float = 80.,
            max_freq: float = 8000.,
            bands: int = 40,
            bandwidth: float = 0.8,
            bandpass_filter_order: int = 3,
            bandpass_filter_kwargs: KWArgs = None,
            envelope_follower_freq: float = 50.,
            envelope_follower_kwargs: KWArgs = None,
            dry: float = 0.,
            wet: float = 1.,
    ) -> 'Vocoder':
        """
        Builds a Vocoder instance.

        Args:
            carrier_freq (float):
                Frequency of the carrier wave in Hz.
            carrier_wave_builder:
                Defaults to ``SawtoothWave``.
            carrier_wave:
                Optional pre-built carrier wave. If provided, this will
                override ``carrier_freq`` and ``carrier_wave_builder``.
            min_freq (float):
                Minimum frequency of the bandpass filters in Hz.
            max_freq (float):
                Maximum frequency of the bandpass filters in Hz.
                Should be <= half the sample rate of the audio.
            bands (int):
                Number of bands to divide the frequency range into.
                More bands increases reconstruction quality.
            bandwidth (float):
                Bandwidth of each band, as a fraction of its maximum width.
                Range: ``(0, 1]``.
            bandpass_filter_order (int):
                Bandpass filter order. Higher orders have steeper rolloffs.
            bandpass_filter_kwargs:
                Optional keyword arguments to pass to the
                bandpass filter builder.
            envelope_follower_freq (float):
                Cutoff frequency of the envelope follower in Hz.
            envelope_follower_kwargs:
                Optional keyword arguments to pass to the
                envelope follower filter builder.
            dry:
                Dry (input) signal level. 0 is none, 1 is unity.
            wet:
                Wet (affected) signal level. 0 is none, 1 is unity.
        """

        carrier_wave = carrier_wave or carrier_wave_builder(carrier_freq)

        bandpass_filters = []
        alpha = np.log2(max_freq / min_freq)
        for band in range(bands):
            f = min_freq * 2 ** (alpha * band / bands)
            f_next = min_freq * 2 ** (alpha * (band + 1) / bands)
            width = bandwidth * (f_next - f)

            bandpass_filters.append(
                Filter.build(
                    'bandpass',
                    freq=center_to_band(f, width),
                    order=bandpass_filter_order,
                    **(bandpass_filter_kwargs or {}),
                )
            )

        envelope_follower = EnvelopeFollower.build(
            envelope_follower_freq,
            **(envelope_follower_kwargs or {}),
        )

        return cls(
            carrier_wave,
            bandpass_filters,
            envelope_follower,
            max_freq,
            dry,
            wet,
        )

    def get_wet_signal(self, audio: Audio) -> np.ndarray:
        carrier = self._get_carrier(audio)

        new_signals = [
            self._get_carrier_signal_for_band(audio, carrier, bpf)
            for bpf in self.bandpass_filters
        ]

        return np.sum(new_signals, axis=0)

    def _get_carrier(self, audio: Audio) -> Audio:
        t = np.arange(len(audio)) * audio.sample_period
        carrier = self.carrier_wave(t)
        return audio.copy(signal=carrier)

    def _get_carrier_signal_for_band(self, modulator: Audio, carrier: Audio, bpf: Filter) -> np.ndarray:
        try:
            filtered_modulator = bpf(modulator.copy())
        except ValueError:
            sample_rate = modulator.sample_rate
            warnings.warn(
                f'Received audio with sample_rate={sample_rate}, which is too '
                f'low for Vocoder with max_freq={self.max_freq}; '
                f'band(s) will be dropped, reducing quality. '
                f'To fix, either 1) build the Vocoder with '
                f'max_freq <= sample_rate / 2 = {sample_rate / 2}, '
                f'or 2) use a TTS engine with a '
                f'sample_rate >= 2 * max_freq = {2 * self.max_freq}.'
            )

            return np.zeros_like(modulator.signal)

        modulator_level = self.envelope_follower(filtered_modulator).signal

        carrier_signal = bpf(carrier.copy()).signal
        carrier_signal *= modulator_level

        return carrier_signal
