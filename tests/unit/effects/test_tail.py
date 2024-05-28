import unittest

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.tail import Tail


class TailTest(unittest.TestCase):
    def test_tail(self):
        audio = Audio(signal=np.array([1., 2., 3.]), sample_rate=1)

        tail = Tail(seconds=1.5)

        result = tail.apply(audio.copy())

        self.assertEqual(
            Audio(signal=np.array([1., 2., 3., 0., 0.]), sample_rate=1),
            result,
        )

    def test_tail_zero_seconds(self):
        audio = Audio(signal=np.array([1., 2., 3.]), sample_rate=1)

        tail = Tail(seconds=0.)

        result = tail.apply(audio.copy())

        self.assertEqual(audio, result)
