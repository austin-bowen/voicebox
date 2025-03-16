import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from unit.utils import build_audio
from voicebox.tts import Pyttsx3TTS


class PicoTTSTest(unittest.TestCase):
    def setUp(self):
        self.audio = build_audio()

        self.tmp_file = '/some/tmp/file.wav'

        self.mock_engine = Mock()
        self.text = 'foo bar'

        self.tts = Pyttsx3TTS(engine=self.mock_engine)

    def test_constructor_defaults(self):
        self.assertIs(self.tts.engine, self.mock_engine)
        self.assertEqual('voicebox-pyttsx3-', self.tts.temp_file_prefix)
        self.assertIsNone(self.tts.temp_file_dir)

    @patch('voicebox.tts.tts.NamedTemporaryFile')
    @patch('voicebox.tts.tts.get_audio_from_wav_file')
    def test_get_speech_with_constructor_defaults(self, *mocks):
        self._setup_mocks(*mocks)

        result = self.tts.get_speech(self.text)

        self.assertIs(result, self.audio)

        self._check_mock_calls()

    def _setup_mocks(
            self,
            mock_get_audio_from_wav_file,
            mock_NamedTemporaryFile,
    ):
        mock_get_audio_from_wav_file.return_value = self.audio
        self.mock_get_audio_from_wav_file = mock_get_audio_from_wav_file

        mock_NamedTemporaryFile.return_value.__enter__ = mock_NamedTemporaryFile
        mock_NamedTemporaryFile.return_value.name = self.tmp_file

    def _check_mock_calls(self):
        self.mock_engine.save_to_file.assert_called_once_with(
            self.text,
            self.tmp_file,
        )

        self.mock_engine.runAndWait.assert_called_once()

        self.mock_get_audio_from_wav_file.assert_called_once_with(
            Path(self.tmp_file),
        )
