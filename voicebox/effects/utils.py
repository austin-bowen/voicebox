from dataclasses import dataclass
from typing import Callable, Tuple, Any

import numpy as np

from voicebox.types import KWArgs


def db(db_: float) -> float:
    """Decibels to gain. db(0) --> 1; db(-6) --> 0.501; db(+6) --> 1.995."""
    return 10 ** (db_ / 20)


def get_crossover_points(signal: np.ndarray, boundary: float = 'mean') -> np.ndarray:
    """Returns the indices of the points just before the signal crosses the boundary."""
    boundary = signal.mean() if boundary == 'mean' else boundary
    signal = signal - boundary
    return np.where(np.diff(np.sign(signal)) != 0)[0]


@dataclass
class CallCache:
    """
    Caches the most recent function call. If the next call's function
    and args match the previous, then the last result will be returned,
    and the function will not be run. This is useful e.g. for caching
    values derived from a class's instance variables.

    Example:

    >>> def add(a, b=1):
    >>>     print(f'Called with {a} and {b}')
    >>>     return a + b
    >>>
    >>> cached_add = CallCache(add)
    >>> print(cached_add(1, b=1))
    Called with 1 and 1
    2
    >>> print(cached_add(1, b=1)) # Called with same args; cached value returned
    2
    >>> print(cached_add(2, b=3)) # New args; function is called
    Called with 2 and 3
    5
    """

    func: Callable

    _prev_key: Tuple[Tuple, KWArgs] = None
    _prev_result: Any = None

    def __call__(self, *args, **kwargs):
        key = (args, kwargs)

        if key != self._prev_key:
            self._prev_key = key
            self._prev_result = self.func(*args, **kwargs)

        return self._prev_result
