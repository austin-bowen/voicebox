import unittest
from unittest.mock import Mock, call

from parameterized import parameterized

from unit.utils import assert_called_with_exactly, build_audio
from voicebox.tts import TTS, FallbackTTS, RetryTTS

log = Mock()


class TTSTest(unittest.TestCase):
    def test_call(self):
        class TestTTS(TTS):
            def get_speech(self, text):
                return text

        audio = Mock()

        tts = TestTTS()
        tts.get_speech = Mock()
        tts.get_speech.side_effect = lambda _: audio

        result = tts('foo')

        self.assertEqual(result, audio)

        tts.get_speech.assert_called_once_with('foo')


class FallbackTTSTest(unittest.TestCase):
    def test_get_speech_returns_first_good_tts_response(self):
        audio = build_audio()

        bad_tts_1 = build_bad_tts()
        bad_tts_2 = build_bad_tts()

        good_tts_1 = Mock()
        good_tts_1.get_speech.side_effect = lambda text: audio

        good_tts_2 = Mock()

        tts = FallbackTTS(
            [bad_tts_1, bad_tts_2, good_tts_1, good_tts_2],
            log=log,
        )

        result = tts.get_speech('foo')

        self.assertIs(result, audio)

        for mock_tts in [bad_tts_1, bad_tts_2, good_tts_1]:
            mock_tts.get_speech.assert_called_once_with('foo')

        good_tts_2.get_speech.assert_not_called()

    def test_get_speech_raises_exception_if_all_ttss_fail(self):
        bad_tts_1 = build_bad_tts()
        bad_tts_2 = build_bad_tts()

        tts = FallbackTTS([bad_tts_1, bad_tts_2], log=log)

        self.assertRaises(Exception, tts.get_speech, 'foo')

        bad_tts_1.get_speech.assert_called_once_with('foo')
        bad_tts_2.get_speech.assert_called_once_with('foo')

    def test_get_speech_with_empty_ttss_raises_ValueError(self):
        tts = FallbackTTS([], log=log)
        self.assertRaises(ValueError, tts.get_speech, 'foo')


class RetryTTSTest(unittest.TestCase):
    def test_max_attempts_defaults_to_3(self):
        tts = RetryTTS(tts=Mock())
        self.assertEqual(3, tts.max_attempts)

    def test_get_speech_returns_first_successful_attempt(self):
        audio = build_audio()

        def mock_get_speech(text):
            mock_get_speech.call_count += 1
            call_count = mock_get_speech.call_count

            if call_count == 1:
                raise Exception('First call fails')
            else:
                return audio

        mock_tts = Mock()
        mock_tts.get_speech.side_effect = mock_get_speech
        mock_get_speech.call_count = 0

        tts = RetryTTS(mock_tts, log=log)

        result = tts.get_speech('foo')

        self.assertIs(result, audio)

        calls = [call('foo')] * 2
        assert_called_with_exactly(mock_tts.get_speech, calls)

    def test_get_speech_raises_exception_on_last_failed_attempt(self):
        mock_tts = build_bad_tts()

        tts = RetryTTS(mock_tts, log=log)

        self.assertRaises(Exception, tts.get_speech, 'foo')

        calls = [call('foo')] * tts.max_attempts
        assert_called_with_exactly(mock_tts.get_speech, calls)

    @parameterized.expand([0, -1])
    def test_get_speech_with_non_positive_max_attempts_raises_ValueError(
            self,
            max_attempts: int,
    ):
        tts = RetryTTS(tts=Mock(), max_attempts=max_attempts, log=log)
        self.assertRaises(ValueError, tts.get_speech, 'foo')


def build_bad_tts() -> TTS:
    def raise_exception(*unused):
        raise Exception('Whoopsiedoodle!')

    bad_tts = Mock()
    bad_tts.get_speech.side_effect = raise_exception

    return bad_tts
