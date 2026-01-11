import unittest
from unittest.mock import Mock, patch

from google.api_core import gapic_v1
from google.cloud.texttospeech import (
    AudioConfig,
    AudioEncoding,
    SynthesisInput,
)
from parameterized import parameterized

from unit.utils import build_audio
from voicebox.ssml import SSML
from voicebox.tts.googlecloudtts import GoogleCloudTTS


class GoogleCloudTTSTest(unittest.TestCase):
    def setUp(self):
        response = Mock()
        response.audio_content = b"audio_content"

        self.client = Mock()
        self.client.synthesize_speech.return_value = response

        self.voice_params = Mock()

        self.tts = GoogleCloudTTS(self.client, self.voice_params)

    def test_constructor_defaults(self):
        self.assertIs(self.tts.client, self.client)
        self.assertIs(self.tts.voice_params, self.voice_params)
        self.assertEqual(AudioConfig(), self.tts.audio_config)
        self.assertIs(gapic_v1.method.DEFAULT, self.tts.timeout)

    def test_constructor(self):
        audio_config = AudioConfig(speaking_rate=0.25)
        timeout = 3.14

        tts = GoogleCloudTTS(
            self.client,
            self.voice_params,
            audio_config,
            timeout,
        )

        self.assertIs(tts.client, self.client)
        self.assertIs(tts.voice_params, self.voice_params)
        self.assertIs(audio_config, tts.audio_config)
        self.assertIs(timeout, tts.timeout)

    @parameterized.expand([False, True])
    @patch("voicebox.tts.googlecloudtts.get_audio_from_wav_file")
    def test_get_speech(self, is_ssml: bool, mock_get_audio_from_wav_file):
        audio = build_audio()
        mock_get_audio_from_wav_file.return_value = audio

        text = SSML("foo") if is_ssml else "foo"
        result = self.tts.get_speech(text)

        self.assertIs(result, audio)

        expected_input = (
            SynthesisInput(ssml="foo") if is_ssml else SynthesisInput(text="foo")
        )

        self.client.synthesize_speech.assert_called_once_with(
            input=expected_input,
            voice=self.tts.voice_params,
            audio_config=self.tts.audio_config,
            timeout=self.tts.timeout,
        )

        self.assertEqual(
            AudioEncoding.LINEAR16,
            self.tts.audio_config.audio_encoding,
        )
