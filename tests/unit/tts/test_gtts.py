import unittest
from unittest.mock import patch

from unit.utils import assert_first_call, build_audio
from voicebox.ssml import SSML
from voicebox.tts.gtts import gTTS


class gTTSTest(unittest.TestCase):
    def test_constructor_defaults(self):
        tts = gTTS()
        self.assertDictEqual({}, tts.gtts_kwargs)

    def test_constructor_with_kwargs(self):
        tts = gTTS(foo='bar', one=1)
        self.assertDictEqual(dict(foo='bar', one=1), tts.gtts_kwargs)

    @patch('voicebox.tts.tts.get_audio_from_mp3')
    @patch('voicebox.tts.gtts.gTTS_')
    def test_get_speech(self, mock_gTTS, mock_get_audio_from_mp3):
        audio = build_audio()
        mock_get_audio_from_mp3.return_value = audio

        tts = gTTS(key='value')

        result = tts.get_speech('foo')

        self.assertIs(result, audio)

        assert_first_call(mock_gTTS, 'foo', key='value')
        mock_gTTS.return_value.write_to_fp.assert_called_once()
        mock_get_audio_from_mp3.assert_called_once()

    def test_get_speech_with_SSML_raises_ValueError(self):
        tts = gTTS()
        with self.assertRaises(ValueError):
            tts.get_speech(SSML('<speak>foo</speak>'))
