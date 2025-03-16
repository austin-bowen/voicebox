import unittest
from unittest.mock import Mock, patch

from elevenlabs.client import ElevenLabs

from unit.utils import build_audio
from voicebox.tts.elevenlabs import ElevenLabsTTS


class ElevenLabsTest(unittest.TestCase):
    def setUp(self):
        self.tmp_file = '/some/tmp/file.wav'

        self.audio = build_audio()

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
        self.assertIsNone(tts.temp_file_dir)
        self.assertEqual('voicebox-elevenlabs-', tts.temp_file_prefix)

    def test_constructor(self):
        self.assertIs(self.tts.client, self.client)
        self.assertIs(self.tts.voice, self.voice)
        self.assertIs(self.tts.model, self.model)

    @patch('voicebox.tts.tts.get_audio_from_mp3')
    def test_get_speech(self, mock_get_audio_from_mp3):
        mock_get_audio_from_mp3.return_value = self.audio

        result = self.tts.get_speech('foo')

        self.assertIs(result, self.audio)

        self.client.generate.assert_called_once_with(
            text='foo',
            voice=self.voice,
            model=self.model,
        )

        mock_get_audio_from_mp3.assert_called_once()

    @patch('voicebox.tts.tts.get_audio_from_mp3')
    def test_get_speech_with_defaults(self, mock_get_audio_from_mp3):
        mock_get_audio_from_mp3.return_value = self.audio
        self.tts = ElevenLabsTTS(self.client)

        result = self.tts.get_speech('foo')

        self.assertIs(result, self.audio)
        self.client.generate.assert_called_once_with(text='foo')
        mock_get_audio_from_mp3.assert_called_once()
