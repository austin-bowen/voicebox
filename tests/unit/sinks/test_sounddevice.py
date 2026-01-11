import unittest
from unittest.mock import patch

from parameterized import parameterized

from unit.utils import build_audio
from voicebox.sinks.sounddevice import SoundDevice, Device, Latency


class SoundDeviceTest(unittest.TestCase):
    def test_constructor_defaults(self):
        sink = SoundDevice()
        self.assertIsNone(sink.device)
        self.assertTrue(sink.blocking)
        self.assertEqual(0.1, sink.latency)

    @parameterized.expand(
        [
            (None, True, 0.1),
            ("some-device", False, "low"),
        ]
    )
    @patch("voicebox.sinks.sounddevice.sd")
    def test_play(
        self,
        device: Device,
        blocking: bool,
        latency: Latency,
        mock_sd,
    ):
        audio = build_audio()

        sink = SoundDevice(device, blocking, latency)
        sink.play(audio)

        mock_sd.play.assert_called_once()
        mock_call = mock_sd.play.mock_calls[0]

        self.assertEqual(2, len(mock_call.args))
        self.assertIs(mock_call.args[0], audio.signal)
        self.assertEqual(audio.sample_rate, mock_call.args[1])

        self.assertEqual(3, len(mock_call.kwargs))
        self.assertEqual(blocking, mock_call.kwargs["blocking"])
        self.assertEqual(device, mock_call.kwargs["device"])
        self.assertEqual(latency, mock_call.kwargs["latency"])
