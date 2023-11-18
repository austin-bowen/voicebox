import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tests.utils import build_audio, assert_first_call
from voicebox.tts.picotts import PicoTTS


class PicoTTSTest(unittest.TestCase):
    def setUp(self):
        self.mock_proc = Mock()
        self.audio = build_audio()

        self.tmp_file = '/some/tmp/file.wav'

    def test_constructor_defaults(self):
        tts = PicoTTS()
        self.assertEqual('pico2wave', tts.pico2wave_path)
        self.assertIsNone(tts.language)
        self.assertEqual('voicebox-pico-tts-', tts.temp_wav_file_prefix)
        self.assertIsNone(tts.temp_wav_file_dir)

    @patch('tempfile.NamedTemporaryFile')
    @patch('voicebox.tts.picotts.get_audio_from_wav_file')
    @patch('subprocess.run')
    def test_get_speech_with_constructor_defaults(self, *mocks):
        self._setup_mocks(*mocks)

        tts = PicoTTS()

        result = tts.get_speech('foo bar')

        self.assertIs(result, self.audio)

        expected_args = [
            'pico2wave',
            '-w', self.tmp_file,
            'foo bar',
        ]

        self._check_mock_calls(expected_args)

    @patch('tempfile.NamedTemporaryFile')
    @patch('voicebox.tts.picotts.get_audio_from_wav_file')
    @patch('subprocess.run')
    def test_get_speech_with_custom_config_and_SSML_text(self, *mocks):
        self._setup_mocks(*mocks)

        tts = PicoTTS(
            pico2wave_path='/path/to/pico2wave',
            language='en-US',
        )

        result = tts.get_speech('foo bar')

        self.assertIs(result, self.audio)

        expected_args = [
            '/path/to/pico2wave',
            '-w', self.tmp_file,
            '-l', 'en-US',
            'foo bar',
        ]

        self._check_mock_calls(expected_args)

    @patch('tempfile.NamedTemporaryFile')
    @patch('voicebox.tts.picotts.get_audio_from_wav_file')
    @patch('subprocess.run')
    def test_get_speech_without_pico2wave_installed_raises_FileNotFoundError(self, *mocks):
        self._setup_mocks(*mocks)
        self.mock_run.side_effect = FileNotFoundError('File not found')

        tts = PicoTTS()

        self.assertRaises(FileNotFoundError, tts.get_speech, 'foo bar')

    def _setup_mocks(
            self,
            mock_run,
            mock_get_audio_from_wav_file,
            mock_NamedTemporaryFile,
    ):
        self.mock_run = mock_run

        mock_get_audio_from_wav_file.return_value = self.audio
        self.mock_get_audio_from_wav_file = mock_get_audio_from_wav_file

        mock_NamedTemporaryFile.return_value.__enter__ = mock_NamedTemporaryFile
        mock_NamedTemporaryFile.return_value.name = self.tmp_file

    def _check_mock_calls(self, run_args):
        assert_first_call(
            self.mock_run,
            run_args,
            check=True,
        )

        self.mock_get_audio_from_wav_file.assert_called_once_with(
            Path(self.tmp_file),
        )
