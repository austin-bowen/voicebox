from unittest import TestCase
from unittest.mock import Mock

from voicebox.sinks.sink import Sink


class SinkTest(TestCase):
    def test_call(self):
        class TestSink(Sink):
            def play(self, audio_):
                pass

        sink = TestSink()
        sink.play = Mock()
        audio = Mock()

        sink(audio)

        sink.play.assert_called_once_with(audio)
