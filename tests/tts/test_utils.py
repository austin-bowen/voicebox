import unittest
from typing import List
from unittest.mock import Mock

import numpy as np
from parameterized import parameterized

from voicebox.tts.utils import (
    add_optional_items,
    get_audio_from_audio_segment,
)


class GetAudioFromAudioSegmentTest(unittest.TestCase):
    @parameterized.expand([
        (
                1,
                [0, 1, -2, 127, -128],
                [0., 0.0078125, -0.015625, 0.9921875, -1.],
        ),
        (
                2,
                [0, 1024, -2048, 32767, -32768],
                [0., 0.03125, -0.0625, 0.999969482, -1.],
        ),
        (
                4,
                [0, 33554432, -67108864, 2147483647, -2147483648],
                [0., 0.015625, -0.03125, 1., -1.],
        ),
    ])
    def test(
            self,
            frame_width: int,
            samples: List[int],
            expected_signal: List[float],
    ):
        frame_rate = 44100

        audio_segment = Mock()
        audio_segment.frame_rate = frame_rate
        audio_segment.frame_width = frame_width
        audio_segment.get_array_of_samples.return_value = np.array(samples)

        result = get_audio_from_audio_segment(audio_segment)

        np.testing.assert_allclose(result.signal, expected_signal)
        self.assertEqual(np.float32, result.signal.dtype)
        self.assertEqual(frame_rate, result.sample_rate)


class AddOptionalItemsTest(unittest.TestCase):
    def test(self):
        d = {'foo': 1}

        add_optional_items(d, [('bar', None), ('baz', 3)])

        self.assertDictEqual({'foo': 1, 'baz': 3}, d)
