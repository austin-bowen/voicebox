import unittest
from io import BytesIO
from unittest.mock import Mock, patch

import numpy as np
from parameterized import parameterized

from voicebox.audio import Audio
from voicebox.sinks.wavefile import WaveFile, write_audio_to_wav
from voicebox.tts.utils import get_audio_from_wav_file


class WaveFileTest(unittest.TestCase):
    def setUp(self):
        self.file = Mock()
        self.sink = WaveFile(self.file)

    def test_constructor_defaults(self):
        self.assertIs(self.sink.file, self.file)
        self.assertFalse(self.sink.append)
        self.assertEqual(2, self.sink.sample_width)

    def test_constructor(self):
        file = Mock()
        sink = WaveFile(file, append=True, sample_width=4)

        self.assertIs(sink.file, file)
        self.assertTrue(sink.append)
        self.assertEqual(4, sink.sample_width)

    @patch('voicebox.sinks.wavefile.write_audio_to_wav')
    def test_play(self, mock_write_audio_to_wav):
        audio = Mock()

        self.sink.play(audio)

        mock_write_audio_to_wav.assert_called_once_with(
            audio,
            self.file,
            append=False,
            sample_width=2,
        )


class WriteAudioToWavTest(unittest.TestCase):
    @parameterized.expand([
        (1, [-1., 0., .5, 0.992187]),
        (2, [-1., 0., .5, 0.9999695]),
        (4, [-1., 0., .5, 1.]),
    ])
    def test(self, sample_width: int, expected_signal):
        audio = Audio(
            signal=np.float32([-1., 0., .5, 1.]),
            sample_rate=44100,
        )

        with BytesIO() as file:
            write_audio_to_wav(audio, file, sample_width=sample_width)
            file.seek(0)

            result = get_audio_from_wav_file(file)

        expected_audio = Audio(
            signal=np.float32(expected_signal),
            sample_rate=audio.sample_rate,
        )

        self.assertEqual(result, expected_audio)
