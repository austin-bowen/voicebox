import unittest
from typing import Sequence
from unittest.mock import Mock, call

import numpy as np

from voicebox.audio import Audio


def assert_called_with_exactly(mock: Mock, calls: Sequence['call']) -> None:
    """Assert a mock was called with exactly the given calls, in order."""
    t = unittest.TestCase()
    t.assertSequenceEqual(calls, mock.mock_calls)


def build_audio(signal_len: int = 1, sample_rate: int = 44100) -> Audio:
    return Audio(np.zeros(signal_len, dtype=np.float32), sample_rate)
