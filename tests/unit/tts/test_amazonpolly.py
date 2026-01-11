import unittest
from unittest.mock import Mock, patch

import numpy as np
from mypy_boto3_polly.literals import VoiceIdType

from unit.utils import build_audio
from voicebox.ssml import SSML
from voicebox.tts.amazonpolly import AmazonPolly


class AmazonPollyTest(unittest.TestCase):
    def setUp(self):
        self.samples = np.int16([0, 1, 20, 300, 4000])

        audio_stream = Mock()
        audio_stream.read.return_value = self.samples.tobytes()

        response = {"AudioStream": audio_stream}

        self.client = Mock()
        self.client.synthesize_speech.return_value = response

        self.voice_id: VoiceIdType = "Aditi"

        self.tts = AmazonPolly(self.client, self.voice_id)

    def test_constructor_defaults(self):
        self.assertIs(self.tts.client, self.client)
        self.assertIs(self.tts.voice_id, self.voice_id)
        self.assertIsNone(self.tts.engine)
        self.assertIsNone(self.tts.language_code)
        self.assertIsNone(self.tts.lexicon_names)
        self.assertEqual(16000, self.tts.sample_rate)

    def test_constructor(self):
        lexicon_names = ["lex", "names"]

        self.tts = AmazonPolly(
            self.client,
            self.voice_id,
            engine="neural",
            language_code="en-US",
            lexicon_names=lexicon_names,
            sample_rate=8000,
        )

        self.assertIs(self.tts.client, self.client)
        self.assertIs(self.tts.voice_id, self.voice_id)
        self.assertIs(self.tts.engine, "neural")
        self.assertIs(self.tts.language_code, "en-US")
        self.assertIs(self.tts.lexicon_names, lexicon_names)
        self.assertEqual(8000, self.tts.sample_rate)

    @patch("voicebox.tts.amazonpolly.get_audio_from_samples")
    def test_get_speech_with_default_settings(self, mock_get_audio_from_samples):
        audio = build_audio()
        mock_get_audio_from_samples.return_value = audio

        result = self.tts.get_speech("foo")

        self.assertIs(result, audio)

        self.client.synthesize_speech.assert_called_once_with(
            OutputFormat="pcm",
            Text="foo",
            VoiceId=self.voice_id,
            SampleRate="16000",
            TextType="text",
        )

        mock_get_audio_from_samples.assert_called_once()
        mock_call = mock_get_audio_from_samples.mock_calls[0]
        np.testing.assert_allclose(mock_call.args[0], self.samples)

    @patch("voicebox.tts.amazonpolly.get_audio_from_samples")
    def test_get_speech_with_custom_settings(self, mock_get_audio_from_samples):
        audio = build_audio()
        mock_get_audio_from_samples.return_value = audio

        lexicon_names = ["lex", "names"]

        self.tts = AmazonPolly(
            self.client,
            self.voice_id,
            engine="neural",
            language_code="en-US",
            lexicon_names=lexicon_names,
            sample_rate=8000,
        )

        result = self.tts.get_speech(SSML("foo"))

        self.assertIs(result, audio)

        self.client.synthesize_speech.assert_called_once_with(
            OutputFormat="pcm",
            Text="foo",
            VoiceId=self.voice_id,
            SampleRate="8000",
            TextType="ssml",
            Engine="neural",
            LanguageCode="en-US",
            LexiconNames=lexicon_names,
        )

        mock_get_audio_from_samples.assert_called_once()
        mock_call = mock_get_audio_from_samples.mock_calls[0]
        np.testing.assert_allclose(mock_call.args[0], self.samples)
