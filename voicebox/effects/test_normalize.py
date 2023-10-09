from unittest import TestCase

import numpy as np
from parameterized import parameterized

from voicebox.effects.normalize import Normalize
from voicebox.audio import Audio


class NormalizeTest(TestCase):
    def test_max_amplitude_defaults_to_1(self):
        normalize = Normalize()
        self.assertEqual(1.0, normalize.max_amplitude)

    @parameterized.expand([
        (1.0, np.array([0., .25, -.4, .5, -1., .1])),
        (0.5, np.array([0., .125, -.2, .25, -.5, .05])),
        (2, np.array([[0., .5, -.8, 1., -2, .2]])),
    ])
    def test_apply(self, max_amplitude: float, expected_signal: np.ndarray):
        normalize = Normalize(max_amplitude)

        audio = Audio(signal=np.array([0., .5, -.8, 1., -2, .2]), sample_rate=44100)

        result = normalize.apply(audio.copy())

        expected = audio.copy(signal=expected_signal)
        self.assertEqual(expected, result)

    def test_apply_to_zero_signal_returns_zero_signal(self):
        normalize = Normalize()

        audio = Audio(signal=np.array([0., 0., 0.]), sample_rate=44100)

        result = normalize.apply(audio.copy())

        self.assertEqual(audio, result)
