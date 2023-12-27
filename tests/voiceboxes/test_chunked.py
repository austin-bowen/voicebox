import unittest
from unittest.mock import Mock, call

from tests.utils import assert_called_with_exactly
from voicebox.voiceboxes.chunked import ChunkedVoicebox
from voicebox.voiceboxes.splitter import SimpleSentenceSplitter


class ChunkedVoiceboxTest(unittest.TestCase):
    def setUp(self):
        self.wrapped_voicebox = Mock()

        self.splitter = Mock()

        self.chunked_voicebox = ChunkedVoicebox(
            self.wrapped_voicebox,
            self.splitter,
        )

    def test_constructor(self):
        self.assertIs(self.chunked_voicebox.voicebox, self.wrapped_voicebox)
        self.assertIs(self.chunked_voicebox.splitter, self.splitter)

    def test_constructor_defaults(self):
        voicebox = ChunkedVoicebox(self.wrapped_voicebox)

        self.assertIs(voicebox.voicebox, self.wrapped_voicebox)
        self.assertIsInstance(voicebox.splitter, SimpleSentenceSplitter)

    def test_say(self):
        text = 'foo bar'
        self.splitter.split.return_value = ['foo', 'bar']

        self.chunked_voicebox.say(text)

        self.splitter.split.assert_called_once_with(text)

        assert_called_with_exactly(
            self.wrapped_voicebox.say,
            [
                call('foo'),
                call('bar'),
            ],
        )
