import unittest
from unittest.mock import patch

from parameterized import parameterized

from tests.utils import build_audio
from voicebox.sinks.sounddevice import SoundDevice


class SoundDeviceTest(unittest.TestCase):
    def test_constructor_defaults(self):
        sink = SoundDevice()
        self.assertTrue(sink.blocking)

    @parameterized.expand([True, False])
    @patch('voicebox.sinks.sounddevice.sd')
    def test_play(self, blocking: bool, mock_sd):
        audio = build_audio()

        sink = SoundDevice(blocking=blocking)
        sink.play(audio)

        mock_sd.play.assert_called_once()
        mock_call = mock_sd.play.mock_calls[0]

        self.assertEqual(2, len(mock_call.args))
        self.assertIs(mock_call.args[0], audio.signal)
        self.assertEqual(audio.sample_rate, mock_call.args[1])

        self.assertEqual(1, len(mock_call.kwargs))
        self.assertEqual(blocking, mock_call.kwargs['blocking'])
