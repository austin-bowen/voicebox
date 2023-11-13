import importlib
import unittest
from typing import Mapping
from unittest.mock import Mock, call, patch

from parameterized import parameterized

import voicebox.tts.cache
from tests.utils import assert_called_with_exactly, build_audio
from voicebox.audio import Audio
from voicebox.tts.cache import PrerecordedTTS


class PrerecordedTTSTest(unittest.TestCase):
    def setUp(self):
        self.foo_audio = build_audio(1)
        self.bar_audio = build_audio(2)
        self.baz_audio = build_audio(3)

        self.fallback_tts = Mock()
        self.setup_fallback_tts({})

    def tearDown(self):
        reload_tts_cache_module()

    def test_get_speech_with_fallback_tts(self):
        self.setup_fallback_tts({'baz': self.baz_audio})

        tts = PrerecordedTTS(
            texts_to_audios={
                'foo': self.foo_audio,
                'bar': self.bar_audio,
            },
            fallback_tts=self.fallback_tts,
        )

        self.assertIs(tts.get_speech('foo'), self.foo_audio)
        self.assertIs(tts.get_speech('bar'), self.bar_audio)
        self.assertIs(tts.get_speech('baz'), self.baz_audio)

        assert_called_with_exactly(
            self.fallback_tts.get_speech,
            [call('baz')]
        )

    def test_get_speech_without_fallback_tts(self):
        tts = PrerecordedTTS(
            texts_to_audios={
                'foo': self.foo_audio,
                'bar': self.bar_audio,
            },
        )

        self.assertIs(tts.get_speech('foo'), self.foo_audio)
        self.assertIs(tts.get_speech('bar'), self.bar_audio)
        self.assertRaises(KeyError, tts.get_speech, 'baz')

    @parameterized.expand([True, False])
    def test_from_tts(self, use_as_fallback: bool):
        self.setup_fallback_tts({
            'foo': self.foo_audio,
            'bar': self.bar_audio,
            'baz': self.baz_audio,
        })

        tts = PrerecordedTTS.from_tts(
            self.fallback_tts,
            texts=['foo', 'baz'],
            use_as_fallback=use_as_fallback,
        )

        self.assertDictEqual(
            {'foo': self.foo_audio, 'baz': self.baz_audio},
            tts.texts_to_audios
        )

        if use_as_fallback:
            self.assertIs(tts.fallback_tts, self.fallback_tts)
        else:
            self.assertIsNone(tts.fallback_tts)

        assert_called_with_exactly(
            self.fallback_tts.get_speech,
            [call('foo'), call('baz')],
        )

    @patch('voicebox.tts.utils.get_audio_from_wav_file')
    def test_from_wav_files(self, get_audio_from_wav_file):
        reload_tts_cache_module()

        get_audio_from_wav_file.side_effect = lambda file: {
            'foo.wav': self.foo_audio,
            'bar.wav': self.bar_audio,
        }[file]

        tts = PrerecordedTTS.from_wav_files(
            texts_to_files={
                'foo': 'foo.wav',
                'bar': 'bar.wav',
            },
            fallback_tts=self.fallback_tts,
        )

        self.assertDictEqual(
            {'foo': self.foo_audio, 'bar': self.bar_audio},
            tts.texts_to_audios,
        )

        self.assertIs(tts.fallback_tts, self.fallback_tts)

        assert_called_with_exactly(
            get_audio_from_wav_file,
            [call('foo.wav'), call('bar.wav')],
        )

    def setup_fallback_tts(self, texts_to_audios: Mapping[str, Audio]) -> None:
        self.fallback_tts.get_speech.side_effect = lambda text: texts_to_audios[text]


def reload_tts_cache_module() -> None:
    importlib.reload(voicebox.tts.cache)


if __name__ == '__main__':
    unittest.main()
