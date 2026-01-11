import unittest
from unittest.mock import Mock, patch

from unit.utils import build_audio
from voicebox.tts.voiceai import VoiceAiTTS


class VoiceAiTest(unittest.TestCase):
    def setUp(self):
        self.audio = build_audio()

        self.api_key = "api-key"

        self.tts = VoiceAiTTS(
            api_key=self.api_key,
            voice_id="voice-id",
            temperature=2.0,
            top_p=1.0,
            model="model",
            language="language",
            api_url="api-url",
            extra_json={"extra_json": "EXTRA-JSON"},
            extra_headers={"Extra-Header": "EXTRA-HEADER"},
            request_kwargs={"request_kwarg": "REQUEST_KWARG"},
        )

    def test_constructor_defaults(self):
        tts = VoiceAiTTS(self.api_key)

        self.assertEqual(self.api_key, tts.api_key)
        self.assertIsNone(tts.voice_id)
        self.assertIsNone(tts.temperature)
        self.assertIsNone(tts.top_p)
        self.assertIsNone(tts.model)
        self.assertIsNone(tts.language)
        self.assertEqual("https://dev.voice.ai/api/v1/tts/speech", tts.api_url)
        self.assertEqual({}, tts.extra_json)
        self.assertEqual({}, tts.extra_headers)
        self.assertEqual({}, tts.request_kwargs)

    def test_constructor(self):
        tts = self.tts

        self.assertEqual(self.api_key, tts.api_key)
        self.assertEqual("voice-id", tts.voice_id)
        self.assertEqual(2.0, tts.temperature)
        self.assertEqual(1.0, tts.top_p)
        self.assertEqual("model", tts.model)
        self.assertEqual("language", tts.language)
        self.assertEqual("api-url", tts.api_url)
        self.assertEqual({"extra_json": "EXTRA-JSON"}, tts.extra_json)
        self.assertEqual({"Extra-Header": "EXTRA-HEADER"}, tts.extra_headers)
        self.assertEqual({"request_kwarg": "REQUEST_KWARG"}, tts.request_kwargs)

    @patch("voicebox.tts.voiceai.get_audio_from_wav_file")
    @patch("voicebox.tts.voiceai.requests")
    def test_get_speech(self, mock_requests, mock_get_audio_from_wav_file):
        response = Mock()
        response.content = b"audio"

        mock_requests.post.return_value = response

        mock_get_audio_from_wav_file.return_value = self.audio

        result = self.tts.get_speech("hello world")

        self.assertIs(result, self.audio)

        mock_requests.post.assert_called_once_with(
            "api-url",
            headers={
                "Authorization": "Bearer api-key",
                "Content-Type": "application/json",
                "Extra-Header": "EXTRA-HEADER",
            },
            json={
                "text": "hello world",
                "audio_format": "wav",
                "voice_id": "voice-id",
                "temperature": 2.0,
                "top_p": 1.0,
                "model": "model",
                "language": "language",
                "extra_json": "EXTRA-JSON",
            },
            request_kwarg="REQUEST_KWARG",
        )

        response.raise_for_status.assert_called_once()
        mock_get_audio_from_wav_file.assert_called_once()

    @patch("voicebox.tts.voiceai.get_audio_from_wav_file")
    @patch("voicebox.tts.voiceai.requests")
    def test_get_speech_with_defaults(self, mock_requests, mock_get_audio_from_wav_file):
        response = Mock()
        response.content = b"audio"

        mock_requests.post.return_value = response

        mock_get_audio_from_wav_file.return_value = self.audio

        tts = VoiceAiTTS(self.api_key)

        result = tts.get_speech("hello world")

        self.assertIs(result, self.audio)

        mock_requests.post.assert_called_once_with(
            "https://dev.voice.ai/api/v1/tts/speech",
            headers={
                "Authorization": "Bearer api-key",
                "Content-Type": "application/json",
            },
            json={
                "text": "hello world",
                "audio_format": "wav",
            },
        )

        response.raise_for_status.assert_called_once()
        mock_get_audio_from_wav_file.assert_called_once()
