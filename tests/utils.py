import unittest
from typing import Sequence
from unittest.mock import Mock, call


def assert_called_with_exactly(mock: Mock, calls: Sequence['call']) -> None:
    """Assert a mock was called with exactly the given calls, in order."""
    t = unittest.TestCase()
    t.assertSequenceEqual(calls, mock.mock_calls)
