import unittest
from unittest.mock import Mock

from unit.utils import build_audio
from voicebox.sinks.distributor import Distributor


class DistributorTest(unittest.TestCase):
    def test_play(self):
        audio = build_audio()

        sinks = [
            mock_sink(),
            mock_sink(),
        ]

        distributor = Distributor(sinks)
        distributor.play(audio)

        for sink in sinks:
            sink.play.assert_called_once_with(audio)


def mock_sink():
    sink = Mock()
    sink.play.side_effect = lambda audio: None
    return sink
