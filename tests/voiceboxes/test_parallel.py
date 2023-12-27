import unittest
from time import sleep
from unittest.mock import Mock, call

from parameterized import parameterized

from tests.utils import assert_called_with_exactly
from voicebox.voiceboxes.parallel import ParallelVoicebox


class ParallelVoiceboxTest(unittest.TestCase):
    def setUp(self):
        self.foo_audio = Mock()
        self.bar_audio = Mock()

        self.tts = Mock()
        self.tts.get_speech.side_effect = lambda it: {
            'foo': self.foo_audio,
            'bar': self.bar_audio,
        }[it]

        self.effect = Mock()
        self.effect.apply.side_effect = lambda it: it
        self.effects = [self.effect]

        self.sink = Mock()

        self.voicebox = ParallelVoicebox.build(
            tts=self.tts,
            effects=self.effects,
            sink=self.sink,
        )

    def tearDown(self):
        self.voicebox.stop()

    def test_build_with_start_False(self):
        self.voicebox = ParallelVoicebox.build(start=False)

        sleep(0.5)
        self.assertFalse(self.voicebox.is_alive())

        self.voicebox.start()
        sleep(0.5)
        self.assertTrue(self.voicebox.is_alive())

    def test_say(self):
        self.voicebox.say('foo')
        self.voicebox.say('bar')
        self.check()

    def test_say_all(self):
        self.voicebox.say_all(['foo', 'bar'])
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
            self.tts.get_speech,
            [
                call('foo'),
                call('bar'),
            ],
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
