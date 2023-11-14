import unittest
from unittest.mock import call, Mock

from tests.utils import assert_called_with_exactly, build_audio
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
            assert_called_with_exactly(sink.play, [call(audio)])


def mock_sink():
    sink = Mock()
    sink.play.side_effect = lambda audio: None
    return sink
