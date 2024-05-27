import unittest
import wave
from io import BytesIO
from typing import List
from unittest.mock import Mock

import numpy as np
from parameterized import parameterized

from voicebox.tts.utils import (
    add_optional_items,
    get_audio_from_audio_segment, get_audio_from_wav_file,
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


class GetAudioFromWavFileTest(unittest.TestCase):
    @parameterized.expand([
        (
                1,
                np.int8([0, 1, -2, 127, -128]),
                [0., 0.0078125, -0.015625, 0.9921875, -1.],
        ),
        (
                2,
                np.int16([0, 1024, -2048, 32767, -32768]),
                [0., 0.03125, -0.0625, 0.999969482, -1.],
        ),
        (
                4,
                np.int32([0, 33554432, -67108864, 2147483647, -2147483648]),
                [0., 0.015625, -0.03125, 1., -1.],
        ),
    ])
    def test(
            self,
            sampwidth: int,
            frames: np.ndarray,
            expected_signal: List[float],
    ):
        framerate = 10_000

        wav_file = self.build_wav(
            sampwidth=sampwidth,
            framerate=framerate,
            frames=frames,
        )

        result = get_audio_from_wav_file(wav_file)

        np.testing.assert_allclose(result.signal, expected_signal)
        self.assertEqual(np.float32, result.signal.dtype)
        self.assertEqual(framerate, result.sample_rate)

    def test_raises_KeyError_when_given_unsupported_sample_width(
            self,
            sampwidth: int = 3,
    ):
        wav_file = self.build_wav(
            sampwidth,
            framerate=10_000,
            frames=np.int8([]),
        )

        self.assertRaises(KeyError, get_audio_from_wav_file, wav_file)

    @staticmethod
    def build_wav(sampwidth: int, framerate: int, frames: np.ndarray) -> BytesIO:
        wav_data = BytesIO()

        with wave.open(wav_data, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(sampwidth)
            wav_file.setframerate(framerate)
            wav_file.writeframes(frames.tobytes())

        wav_data.seek(0)

        return wav_data


class AddOptionalItemsTest(unittest.TestCase):
    def test(self):
        d = {'foo': 1}

        result = add_optional_items(d, [('bar', None), ('baz', 3)])

        self.assertIs(result, d)
        self.assertDictEqual({'foo': 1, 'baz': 3}, d)
