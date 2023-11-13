import importlib
import unittest
from typing import Mapping
from unittest.mock import Mock, call, patch

import cachetools
from parameterized import parameterized

import voicebox.tts.cache
from tests.utils import assert_called_with_exactly, build_audio
from voicebox.audio import Audio
from voicebox.tts.cache import CachedTTS
from voicebox.tts.cache import PrerecordedTTS


class CachedTTSTest(unittest.TestCase):
    def setUp(self):
        self.mock_tts = Mock()
        self.setup_mock_tts({})

    def test_build_defaults(self):
        audio = build_audio(signal_len=10, sample_rate=1)

        tts = CachedTTS.build(self.mock_tts)

        self.assertIs(tts.tts, self.mock_tts)
        self.assertIsInstance(tts.cache, cachetools.LRUCache)
        self.assertEqual(60, tts.cache.maxsize)
        self.assertEqual(audio.len_seconds, tts.cache.getsizeof(audio))
        self.mock_tts.get_speech.assert_not_called()

    def test_build_with_max_size(self):
        audio = build_audio(signal_len=10, sample_rate=1)

        tts = CachedTTS.build(self.mock_tts, max_size=100)

        self.assertIs(tts.tts, self.mock_tts)
        self.assertIsInstance(tts.cache, cachetools.LRUCache)
        self.assertEqual(100, tts.cache.maxsize)
        self.assertEqual(audio.len_seconds, tts.cache.getsizeof(audio))
        self.mock_tts.get_speech.assert_not_called()

    @parameterized.expand([
        ('bytes',),
        ('count',),
        ('seconds',),
    ])
    def test_build_with_size_func_aliases(self, size_func):
        audio = build_audio(signal_len=10, sample_rate=1)

        tts = CachedTTS.build(self.mock_tts, size_func=size_func)

        self.assertIs(tts.tts, self.mock_tts)
        self.assertIsInstance(tts.cache, cachetools.LRUCache)
        self.assertEqual(60, tts.cache.maxsize)

        expected_size = {
            'bytes': audio.len_bytes,
            'count': 1,
            'seconds': audio.len_seconds,
        }[size_func]

        self.assertEqual(expected_size, tts.cache.getsizeof(audio))
        self.mock_tts.get_speech.assert_not_called()

    def test_build_with_cache_class(self):
        audio = build_audio(signal_len=10, sample_rate=1)

        tts = CachedTTS.build(self.mock_tts, cache_class=cachetools.LFUCache)

        self.assertIs(tts.tts, self.mock_tts)
        self.assertIsInstance(tts.cache, cachetools.LFUCache)
        self.assertEqual(60, tts.cache.maxsize)
        self.assertEqual(audio.len_seconds, tts.cache.getsizeof(audio))
        self.mock_tts.get_speech.assert_not_called()

    def test_get_speech_returns_cached_audio(self):
        foo_audio = build_audio(1)
        self.setup_mock_tts({'foo': foo_audio})
        cache = {}

        tts = CachedTTS(self.mock_tts, cache)

        # First call for foo does not exist in cache;
        # second call for foo comes from cache, not mock_tts
        for _ in range(2):
            result = tts.get_speech('foo')
            self.assertIs(foo_audio, result)
            self.assertDictEqual({'foo': foo_audio}, cache)
            assert_called_with_exactly(self.mock_tts.get_speech, [call('foo')])

    def test_get_speech_does_not_cache_audios_too_large(self):
        too_large_audio = build_audio(100)
        self.setup_mock_tts({'too large': too_large_audio})

        tts = CachedTTS.build(self.mock_tts, max_size=1, size_func='bytes')

        result = tts.get_speech('too large')
        self.assertIs(result, too_large_audio)
        self.assertDictEqual({}, dict(tts.cache))
        assert_called_with_exactly(
            self.mock_tts.get_speech,
            [call('too large')],
        )

        result = tts.get_speech('too large')
        self.assertIs(result, too_large_audio)
        self.assertDictEqual({}, dict(tts.cache))
        assert_called_with_exactly(
            self.mock_tts.get_speech,
            [call('too large'), call('too large')],
        )

    def test_get_speech_raises_ValueError_if_not_too_large(self):
        class ErrorCache(dict):
            def __setitem__(self, key, value):
                raise ValueError('Whoopsiedoodle!')

        self.setup_mock_tts({'foo': build_audio()})

        tts = CachedTTS(self.mock_tts, ErrorCache())

        self.assertRaises(ValueError, tts.get_speech, 'foo')

    def setup_mock_tts(self, texts_to_audios: Mapping[str, Audio]) -> None:
        self.mock_tts.get_speech.side_effect = lambda text: texts_to_audios[text]


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
