import unittest
from unittest.mock import Mock, call

from tests.utils import assert_called_with_exactly, build_audio
from voicebox.effects import Normalize
from voicebox.sinks import SoundDevice
from voicebox.tts import PicoTTS
from voicebox.voiceboxes.chunked import ChunkedVoicebox, ParallelChunkedVoicebox
from voicebox.voiceboxes.splitter import SimpleSentenceSplitter


class ChunkedVoiceboxTest(unittest.TestCase):
    chunked_voicebox_class = ChunkedVoicebox

    def test_default_constructor(self):
        voicebox = self.chunked_voicebox_class()

        self.assertIsInstance(voicebox.tts, PicoTTS)

        effects = voicebox.effects
        self.assertEqual(1, len(effects))
        self.assertIsInstance(effects[0], Normalize)

        self.assertIsInstance(voicebox.sink, SoundDevice)

        self.assertIsInstance(voicebox.splitter, SimpleSentenceSplitter)

        return voicebox

    def test_say(self):
        foo_audio = build_audio()
        bar_audio = build_audio()

        tts = Mock()
        tts.get_speech.side_effect = lambda t: {
            'foo': foo_audio,
            'bar': bar_audio,
        }[t]

        sink = Mock()
        sink.play.side_effect = lambda a: None

        splitter = Mock()
        splitter.split.side_effect = lambda t: t.split()

        voicebox = self.chunked_voicebox_class(
            tts=tts,
            sink=sink,
            splitter=splitter,
        )

        voicebox.say('foo bar')

        assert_called_with_exactly(splitter, [call('foo bar')])

        assert_called_with_exactly(
            tts,
            [call('foo'), call('bar')],
        )

        assert_called_with_exactly(
            sink,
            [call(foo_audio), call(bar_audio)]
        )


class ParallelChunkedVoiceboxTest(ChunkedVoiceboxTest):
    chunked_voicebox_class = ParallelChunkedVoicebox

    def test_default_constructor(self):
        voicebox = super().test_default_constructor()
        self.assertEqual(1, voicebox.queue_size)
