import unittest

import numpy as np
from parameterized import parameterized

from tests.utils import build_audio
from voicebox.audio import Audio


class AudioTest(unittest.TestCase):
    def setUp(self):
        self.audio = build_audio(signal_len=100, sample_rate=10)

    def test_len_bytes(self):
        self.assertEqual(4 * 100, self.audio.len_bytes)

    def test_len_seconds(self):
        self.assertAlmostEqual(100 / 10, self.audio.len_seconds)

    def test_period(self):
        self.assertAlmostEqual(1 / 10, self.audio.period)

    def test_set_period(self):
        self.audio.period = 1 / 100
        self.assertAlmostEqual(1 / 100, self.audio.period)
        self.assertAlmostEqual(100, self.audio.sample_rate)

    def test_equal(self):
        self.assertEqual(self.audio, self.audio)
        self.assertEqual(build_audio(100, 10), self.audio)

        self.assertNotEqual(build_audio(101, 10), self.audio)
        self.assertNotEqual(build_audio(100, 11), self.audio)

        other = self.audio.copy()
        self.assertEqual(other, self.audio)
        other.signal[0] = 1.
        self.assertNotEqual(other, self.audio)

    def test_len(self):
        self.assertEqual(100, len(self.audio))

    @parameterized.expand([
        ([], 1),
        ([-1., 0., 1.], 2),
    ])
    def test_check_on_valid_audio_just_returns(self, signal, sample_rate: int):
        audio = Audio(np.float32(signal), sample_rate)
        audio.check()

    @parameterized.expand([
        ([1.0001], 1),
        ([0.], 0),
        ([0.], -1),
    ])
    def test_check_on_invalid_audio_raises_ValueError(self, signal, sample_rate: int):
        audio = Audio(np.float32(signal), sample_rate)
        self.assertRaises(ValueError, audio.check)

    def test_copy(self):
        copy = self.audio.copy()

        self.assertEqual(self.audio, copy)
        self.assertIsNot(copy, self.audio)

        self.assertIsNot(copy.signal, self.audio.signal)
        np.testing.assert_equal(copy.signal, self.audio.signal)

        self.assertEqual(copy.sample_rate, self.audio.sample_rate)

    def test_copy_with_new_signal(self):
        signal = np.array([1., 2., 4., 8.])
        copy = self.audio.copy(signal=signal)

        self.assertIsNot(copy.signal, self.audio.signal)
        self.assertIs(copy.signal, signal)

        self.assertEqual(copy.sample_rate, self.audio.sample_rate)

    def test_copy_with_new_sample_rate(self):
        sample_rate = 42
        copy = self.audio.copy(sample_rate=sample_rate)

        self.assertIsNot(copy.signal, self.audio.signal)
        np.testing.assert_equal(copy.signal, self.audio.signal)

        self.assertEqual(sample_rate, copy.sample_rate)

    def test_empty_audio(self):
        audio = build_audio(signal_len=0)

        self.assertEqual(0, audio.len_bytes)
        self.assertEqual(0, audio.len_seconds)
        self.assertEqual(0, len(audio))
