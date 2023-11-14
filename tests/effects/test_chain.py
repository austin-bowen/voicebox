import unittest
from unittest.mock import Mock

import numpy as np
from parameterized import parameterized

from utils import build_audio
from voicebox.audio import Audio
from voicebox.effects.chain import SeriesChain, ParallelChain


class SeriesChainTest(unittest.TestCase):
    def test_apply(self):
        audio = Audio(np.array([1., 2., 3., 4.]), sample_rate=44100)

        chain = SeriesChain(
            mock_effect(lambda a: a.copy(signal=a.signal + 1)),
            mock_effect(lambda a: a.copy(signal=a.signal * 2)),
        )

        result = chain.apply(audio.copy())

        expected = audio.copy(signal=(audio.signal + 1) * 2)
        self.assertEqual(expected, result)

    def test_apply_with_no_effects_returns_original_audio(self):
        audio = build_audio()
        audio_copy = audio.copy()
        chain = SeriesChain()

        result = chain.apply(audio)

        self.assertIs(result, audio)
        self.assertEqual(audio_copy, result)


class ParallelChainTest(unittest.TestCase):
    def setUp(self):
        self.audio = Audio(np.array([1., 2., 3., 4.]), sample_rate=44100)

        self.chain = ParallelChain(
            mock_effect(lambda a: a.copy(signal=a.signal + 1)),
            mock_effect(lambda a: a.copy(signal=a.signal * 2)),
        )

    def test_constructor_defaults(self):
        chain = ParallelChain()
        self.assertEqual(0., chain.dry_gain)
        self.assertIs(chain.combine_func, np.sum)

    @parameterized.expand([0, 0.5, 1, -1])
    def test_apply(self, dry_gain: float):
        self.chain.dry_gain = dry_gain

        result = self.chain.apply(self.audio.copy())

        expected_signal = (self.audio.signal + 1) + (self.audio.signal * 2)
        if dry_gain > 0:
            expected_signal += dry_gain * self.audio.signal

        expected = self.audio.copy(signal=expected_signal)
        self.assertEqual(expected, result)

    def test_apply_with_mean_combine_func(self):
        self.chain.combine_func = np.mean

        result = self.chain.apply(self.audio.copy())

        expected_signal = (self.audio.signal + 1) + (self.audio.signal * 2)
        expected_signal /= 2

        expected = self.audio.copy(signal=expected_signal)
        self.assertEqual(expected, result)

    def test_apply_raises_RuntimeError_if_sample_rates_differ(self):
        chain = ParallelChain(
            mock_effect(lambda a: a.copy(sample_rate=1)),
            mock_effect(lambda a: a.copy(sample_rate=2)),
        )

        self.assertRaises(RuntimeError, chain.apply, self.audio)

    def test_apply_outputs_signal_with_length_of_longest_subsignal(self):
        chain = ParallelChain(
            mock_effect(lambda a: a.copy(signal=a.signal + 1)),
            mock_effect(lambda a: a.copy(
                signal=np.concatenate([a.signal, a.signal])
            )),
        )

        result = chain.apply(self.audio.copy())

        signal_1 = np.array([2., 3., 4., 5., 0., 0., 0., 0.])
        signal_2 = np.array([1., 2., 3., 4., 1., 2., 3., 4.])
        expected_signal = signal_1 + signal_2

        expected = Audio(expected_signal, sample_rate=self.audio.sample_rate)
        self.assertEqual(expected, result)


def mock_effect(lambda_) -> Mock:
    effect = Mock()
    effect.apply.side_effect = lambda_
    return effect
