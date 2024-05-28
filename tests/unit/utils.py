import unittest
from typing import Sequence
from unittest.mock import Mock, call

import numpy as np

from voicebox.audio import Audio


def assert_called_with_exactly(mock: Mock, calls: Sequence['call']) -> None:
    """Assert a mock was called with exactly the given calls, in order."""
    t = unittest.TestCase()
    t.assertSequenceEqual(calls, mock.mock_calls)


def assert_first_call(mock: Mock, *args, **kwargs) -> None:
    """Asserts the very first call to the mock matches the given call."""
    assert_nth_call(0, mock, *args, **kwargs)


def assert_nth_call(n: int, mock: Mock, *args, **kwargs) -> None:
    """Assert the Nth call to the mock matches the given call."""
    t = unittest.TestCase()
    t.assertSequenceEqual(call(*args, **kwargs), mock.mock_calls[n])


def build_audio(signal_len: int = 1, sample_rate: int = 44100) -> Audio:
    return Audio(np.zeros(signal_len, dtype=np.float32), sample_rate)
