import subprocess
import unittest
from unittest.mock import Mock, patch, call

from tests.utils import build_audio, assert_called_with_exactly, assert_first_call
from voicebox.ssml import SSML
from voicebox.tts import ESpeakNG, ESpeakConfig


class ESpeakNGTest(unittest.TestCase):
    def setUp(self):
        self.mock_proc = Mock()
        self.audio = build_audio()

    def test_constructor_defaults(self):
        tts = ESpeakNG()
        self.assertEqual(ESpeakConfig(), tts.config)

    @patch('voicebox.tts.espeakng.get_audio_from_wav_file')
    @patch('subprocess.Popen')
    def test_get_speech_with_default_config(self, *mocks):
        self._setup_mocks(*mocks)

        config = ESpeakConfig()
        tts = ESpeakNG(config)

        self.assertIs(tts.config, config)

        result = tts.get_speech('foo')

        self.assertIs(result, self.audio)

        expected_args = [
            'espeak-ng',
            '--stdin',
            '-b', '1',
            '--stdout',
        ]

        self._check_mock_calls(expected_args, config)

    @patch('voicebox.tts.espeakng.get_audio_from_wav_file')
    @patch('subprocess.Popen')
    def test_get_speech_with_custom_config_and_SSML_text(self, *mocks):
        self._setup_mocks(*mocks)

        config = ESpeakConfig(
            amplitude=1,
            word_gap_seconds=2.3,
            line_length=4,
            pitch=5,
            speed=6,
            voice='test voice',
            no_final_pause=True,
            exe_path='/path/to/espeak-ng',
            timeout=7.8,
        )

        tts = ESpeakNG(config)

        self.assertIs(tts.config, config)

        result = tts.get_speech(SSML('foo'))

        self.assertIs(result, self.audio)

        expected_args = [
            '/path/to/espeak-ng',
            '--stdin',
            '-b', '1',
            '--stdout',
            '-a', '1',
            '-g', '230',
            '-l', '4',
            '-p', '5',
            '-s', '6',
            '-v', 'test voice',
            '-z',
            '-m',
        ]

        self._check_mock_calls(expected_args, config)

    @patch('voicebox.tts.espeakng.get_audio_from_wav_file')
    @patch('subprocess.Popen')
    def test_get_speech_without_espeakng_installed_raises_FileNotFoundError(self, *mocks):
        self._setup_mocks(*mocks)
        self.mock_Popen.side_effect = FileNotFoundError('File not found')

        tts = ESpeakNG()

        self.assertRaises(FileNotFoundError, tts.get_speech, 'foo')

    def _setup_mocks(
            self,
            mock_Popen,
            mock_get_audio_from_wav_file,
    ):
        mock_Popen.return_value = self.mock_proc
        self.mock_Popen = mock_Popen

        mock_get_audio_from_wav_file.return_value = self.audio
        self.mock_get_audio_from_wav_file = mock_get_audio_from_wav_file

    def _check_mock_calls(self, Popen_args, config):
        assert_first_call(
            self.mock_Popen,
            call(
                Popen_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            ),
        )

        assert_called_with_exactly(
            self.mock_proc.stdin.write,
            [call('foo'.encode('utf-8'))],
        )

        self.mock_proc.stdin.close.assert_called_once()

        assert_called_with_exactly(
            self.mock_get_audio_from_wav_file,
            [call(self.mock_proc.stdout)],
        )

        self.mock_proc.wait.assert_called_once()

        assert_called_with_exactly(
            self.mock_proc.wait,
            [call(timeout=config.timeout)]
        )
