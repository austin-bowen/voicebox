import unittest
from unittest.mock import Mock, call

from unit.utils import assert_called_with_exactly, build_audio
from voicebox.effects.normalize import Normalize
from voicebox.sinks.sounddevice import SoundDevice
from voicebox.tts.picotts import PicoTTS
from voicebox.voiceboxes.simple import SimpleVoicebox


class SimpleVoiceboxTest(unittest.TestCase):
    def setUp(self):
        self.foo_audio = build_audio()
        self.bar_audio = build_audio()

        self.tts = Mock()
        self.tts.get_speech.side_effect = lambda t: {
            'foo': self.foo_audio,
            'bar': self.bar_audio,
        }[t]

        self.effect = Mock()
        self.effect.apply.side_effect = lambda a: a

        self.sink = Mock()
        self.sink.play.side_effect = lambda a: None

        self.voicebox = SimpleVoicebox(self.tts, [self.effect], self.sink)

    def test_constructor_defaults(self):
        voicebox = SimpleVoicebox()

        self.assertIsInstance(voicebox.tts, PicoTTS)

        effects = voicebox.effects
        self.assertEqual(1, len(effects))
        self.assertIsInstance(effects[0], Normalize)

        self.assertIsInstance(voicebox.sink, SoundDevice)

    def test_say(self):
        self.voicebox.say('foo')

        self.tts.get_speech.assert_called_once_with('foo')
        self.effect.apply.assert_called_once_with(self.foo_audio)
        self.sink.play.assert_called_once_with(self.foo_audio)

    def test_say_all(self):
        self.voicebox.say_all(['foo', 'bar'])

        assert_called_with_exactly(self.tts.get_speech, [
            call('foo'), call('bar')
        ])
        assert_called_with_exactly(self.effect.apply, [
            call(self.foo_audio), call(self.bar_audio)
        ])
        assert_called_with_exactly(self.sink.play, [
            call(self.foo_audio), call(self.bar_audio)
        ])
