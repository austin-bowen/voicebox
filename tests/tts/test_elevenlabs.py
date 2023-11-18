import unittest
from unittest.mock import patch

import elevenlabs

from tests.utils import build_audio
from voicebox.tts.elevenlabs import ElevenLabs


class ElevenLabsTest(unittest.TestCase):
    def setUp(self):
        self.api_key = 'API key'
        self.voice = 'voice'
        self.model = 'model'

        self.tts = ElevenLabs(self.api_key, self.voice, self.model)

    def test_constructor_defaults(self):
        tts = ElevenLabs()

        self.assertIsNone(tts.api_key)
        self.assertEqual(elevenlabs.DEFAULT_VOICE, tts.voice)
        self.assertEqual('eleven_monolingual_v1', tts.model)

    def test_constructor(self):
        self.assertIs(self.tts.api_key, self.api_key)
        self.assertIs(self.tts.voice, self.voice)
        self.assertIs(self.tts.model, self.model)

    @patch('voicebox.tts.elevenlabs.get_audio_from_mp3')
    @patch('elevenlabs.generate')
    def test_get_speech(self, mock_generate, mock_get_audio_from_mp3):
        mock_generate.return_value = b'mp3 data'

        audio = build_audio()
        mock_get_audio_from_mp3.return_value = audio

        result = self.tts.get_speech('foo')

        self.assertIs(result, audio)

        mock_generate.assert_called_once_with(
            'foo',
            api_key=self.api_key,
            voice=self.voice,
            model=self.model,
        )

        mock_get_audio_from_mp3.assert_called_once()
