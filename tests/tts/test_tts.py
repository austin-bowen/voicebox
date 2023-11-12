import unittest
from unittest.mock import Mock, call

import numpy as np

from utils import assert_called_with_exactly
from voicebox.audio import Audio
from voicebox.tts import TTS, FallbackTTS


class FallbackTTSTest(unittest.TestCase):
    def test_get_speech(self):
        audio = Audio(np.zeros(1), 1)

        bad_tts_1 = build_bad_tts()
        bad_tts_2 = build_bad_tts()

        good_tts_1 = Mock()
        good_tts_1.get_speech.side_effect = lambda text: audio

        good_tts_2 = Mock()

        tts = FallbackTTS([bad_tts_1, bad_tts_2, good_tts_1, good_tts_2])

        result = tts.get_speech('foo')

        self.assertIs(result, audio)

        for mock_tts in [bad_tts_1, bad_tts_2, good_tts_1]:
            assert_called_with_exactly(mock_tts.get_speech, [call('foo')])

        good_tts_2.get_speech.assert_not_called()


def build_bad_tts() -> TTS:
    def raise_exception(*unused):
        raise RuntimeError('Whoopsiedoodle!')

    bad_tts = Mock()
    bad_tts.get_speech.side_effect = raise_exception

    return bad_tts
