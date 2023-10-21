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
        (1.0, 0., True),
        (1.0, 0., False),
        (1.0, 1., True),
        (1.0, 1., False),
        (2.0, 0., True),
        (2.0, 0., False),
        (2.0, 1., True),
        (2.0, 1., False),
    ])
    def test_apply(self, max_amplitude: float, dc_offset: float, remove_dc_offset: bool):
        normalize = Normalize(max_amplitude=max_amplitude, remove_dc_offset=remove_dc_offset)

        signal = np.array([-1., -.5, 0., .5, 1.]) + dc_offset
        audio = Audio(signal=signal, sample_rate=44100)

        result = normalize.apply(audio.copy())

        actual_max_amplitude = np.abs(result.signal).max()
        self.assertAlmostEqual(max_amplitude, actual_max_amplitude)

        actual_dc_offset = result.signal.mean()
        if not dc_offset or remove_dc_offset:
            self.assertAlmostEqual(0., actual_dc_offset)
        elif dc_offset:
            self.assertNotAlmostEquals(0., actual_dc_offset)

        self.assertEqual(audio.sample_rate, result.sample_rate)

    def test_apply_to_zero_signal_returns_zero_signal(self):
        normalize = Normalize()

        audio = Audio(signal=np.array([0., 0., 0.]), sample_rate=44100)

        result = normalize.apply(audio.copy())

        self.assertEqual(audio, result)
