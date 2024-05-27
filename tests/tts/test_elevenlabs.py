import unittest
from unittest.mock import patch, Mock

from elevenlabs.client import ElevenLabs

from tests.utils import build_audio
from voicebox.tts.elevenlabs import ElevenLabsTTS


class ElevenLabsTest(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.client.generate.return_value = b'mp3 data'

        self.voice = 'voice'
        self.model = 'model'

        self.tts = ElevenLabsTTS(self.client, self.voice, self.model)

    def test_constructor_defaults(self):
        tts = ElevenLabsTTS()

        self.assertIsInstance(tts.client, ElevenLabs)
        self.assertIsNone(tts.voice)
        self.assertIsNone(tts.model)

    def test_constructor(self):
        self.assertIs(self.tts.client, self.client)
        self.assertIs(self.tts.voice, self.voice)
        self.assertIs(self.tts.model, self.model)

    @patch('voicebox.tts.elevenlabs.get_audio_from_mp3')
    def test_get_speech(self, mock_get_audio_from_mp3):
        audio = build_audio()
        mock_get_audio_from_mp3.return_value = audio

        result = self.tts.get_speech('foo')

        self.assertIs(result, audio)

        self.client.generate.assert_called_once_with(
            text='foo',
            voice=self.voice,
            model=self.model,
        )

        mock_get_audio_from_mp3.assert_called_once()

    @patch('voicebox.tts.elevenlabs.get_audio_from_mp3')
    def test_get_speech_with_defaults(self, mock_get_audio_from_mp3):
        self.tts = ElevenLabsTTS(self.client)

        audio = build_audio()
        mock_get_audio_from_mp3.return_value = audio

        result = self.tts.get_speech('foo')

        self.assertIs(result, audio)
        self.client.generate.assert_called_once_with(text='foo')
        mock_get_audio_from_mp3.assert_called_once()
