import unittest
from unittest.mock import Mock, patch

from elevenlabs.client import ElevenLabs

from unit.utils import build_audio
from voicebox.tts.elevenlabs import ElevenLabsTTS


class ElevenLabsTest(unittest.TestCase):
    def setUp(self):
        self.tmp_file = "/some/tmp/file.wav"

        self.audio = build_audio()

        self.voice_id = "voice-id"

        self.client = Mock(ElevenLabs)
        self.client.text_to_speech.convert.return_value = b"mp3 data"

        self.api_key = "api-key"

        self.convert_kwargs = dict(
            model_id="model-id",
        )

        self.tts = ElevenLabsTTS(
            voice_id=self.voice_id,
            client=self.client,
            convert_kwargs=self.convert_kwargs,
        )

    def test_constructor_defaults(self):
        tts = ElevenLabsTTS(voice_id=self.voice_id)

        self.assertIsInstance(tts.client, ElevenLabs)
        self.assertEqual(self.voice_id, tts.voice_id)
        self.assertEqual({}, tts.convert_kwargs)
        self.assertIsNone(tts.temp_file_dir)
        self.assertEqual("voicebox-elevenlabs-", tts.temp_file_prefix)

    def test_constructor(self):
        self.assertIs(self.tts.voice_id, self.voice_id)
        self.assertIs(self.tts.client, self.client)
        self.assertIs(self.tts.convert_kwargs, self.convert_kwargs)

    def test_constructor_builds_client_when_api_key_is_given(self):
        tts = ElevenLabsTTS(
            voice_id=self.voice_id,
            api_key=self.api_key,
        )

        self.assertIsInstance(tts.client, ElevenLabs)
        self.assertEqual(self.api_key, tts.api_key)

    def test_constructor_builds_client_when_client_and_api_key_not_given(self):
        tts = ElevenLabsTTS(
            voice_id=self.voice_id,
        )

        self.assertIsInstance(tts.client, ElevenLabs)

    def test_constructor_raises_ValueError_when_api_key_and_client_are_given(self):
        self.assertRaises(
            ValueError,
            ElevenLabsTTS,
            voice_id=self.voice_id,
            api_key=self.api_key,
            client=self.client,
        )

    @patch("voicebox.tts.tts.get_audio_from_mp3")
    def test_get_speech(self, mock_get_audio_from_mp3):
        mock_get_audio_from_mp3.return_value = self.audio

        result = self.tts.get_speech("hello world")

        self.assertIs(result, self.audio)

        self.client.text_to_speech.convert.assert_called_once_with(
            voice_id=self.voice_id,
            text="hello world",
            model_id="model-id",
        )

        mock_get_audio_from_mp3.assert_called_once()
