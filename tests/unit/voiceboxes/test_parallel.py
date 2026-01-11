import unittest
from time import sleep
from unittest.mock import Mock, call

from parameterized import parameterized

from unit.utils import assert_called_with_exactly
from voicebox.effects import Normalize
from voicebox.sinks import SoundDevice
from voicebox.tts import PicoTTS
from voicebox.voiceboxes.parallel import ParallelVoicebox
from voicebox.voiceboxes.splitter import NoopSplitter


class ParallelVoiceboxTest(unittest.TestCase):
    def setUp(self):
        self.foo_audio = Mock()
        self.bar_audio = Mock()

        self.tts = Mock()
        self.tts.get_speech.side_effect = lambda it: {
            "foo": self.foo_audio,
            "bar": self.bar_audio,
        }[it]

        self.effect = Mock()
        self.effect.apply.side_effect = lambda it: it
        self.effects = [self.effect]

        self.sink = Mock()

        self.text_splitter = Mock()
        self.text_splitter.split.side_effect = lambda it: [it]

        self.voicebox = ParallelVoicebox(
            tts=self.tts,
            effects=self.effects,
            sink=self.sink,
            text_splitter=self.text_splitter,
            queue_get_timeout=0.1,
        )

    def tearDown(self):
        self.voicebox.stop()

    def test_constructor(self):
        self.assertIs(self.voicebox.tts, self.tts)
        self.assertIs(self.voicebox.effects, self.effects)
        self.assertIs(self.voicebox.sink, self.sink)
        self.assertIs(self.voicebox.text_splitter, self.text_splitter)

    def test_constructor_defaults(self):
        voicebox = ParallelVoicebox(start=False)

        self.assertIsInstance(voicebox.tts, PicoTTS)

        effects = voicebox.effects
        self.assertEqual(1, len(effects))
        self.assertIsInstance(effects[0], Normalize)

        self.assertIsInstance(voicebox.sink, SoundDevice)

        self.assertIsInstance(voicebox.text_splitter, NoopSplitter)

    def test_property_setters(self):
        value = Mock()

        self.voicebox.tts = value
        self.assertIs(self.voicebox.tts, value)

        self.voicebox.effects = value
        self.assertIs(self.voicebox.effects, value)

        self.voicebox.sink = value
        self.assertIs(self.voicebox.sink, value)

        self.voicebox.text_splitter = value
        self.assertIs(self.voicebox.text_splitter, value)

    def test_constructor_with_start_False(self):
        self.voicebox = ParallelVoicebox(start=False)

        sleep(0.5)
        self.assertFalse(self.voicebox.is_alive())

        self.voicebox.start()
        sleep(0.5)
        self.assertTrue(self.voicebox.is_alive())

    def test_say(self):
        self.voicebox.say("foo")
        self.voicebox.say("bar")
        self.check()

    def test_say_all(self):
        self.voicebox.say_all(["foo", "bar"])
        self.check()

    @parameterized.expand([True, False])
    def test_stop(self, wait: bool):
        self.assertTrue(self.voicebox.is_alive())

        self.voicebox.stop(wait=wait)

        if not wait:
            self.voicebox.join()

        self.assertFalse(self.voicebox.is_alive())

    def test_context_manager(self):
        with self.voicebox:
            self.assertTrue(self.voicebox.is_alive())

        self.voicebox.join()
        self.assertFalse(self.voicebox.is_alive())

    def check(self):
        self.voicebox.wait_until_done()

        assert_called_with_exactly(
            self.text_splitter.split,
            [call("foo"), call("bar")],
        )

        assert_called_with_exactly(
            self.tts.get_speech,
            [call("foo"), call("bar")],
        )

        assert_called_with_exactly(
            self.effect,
            [
                call(self.foo_audio),
                call(self.bar_audio),
            ],
        )

        assert_called_with_exactly(
            self.sink,
            [
                call(self.foo_audio),
                call(self.bar_audio),
            ],
        )
