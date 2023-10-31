import numpy as np


def db(db_: float) -> float:
    """Decibels to gain. db(0) --> 1; db(-6) --> 0.501; db(+6) --> 1.995."""
    return 10 ** (db_ / 20)


def get_crossover_points(signal: np.ndarray, boundary: float = 'mean') -> np.ndarray:
    """Returns the indices of the points just before the signal crosses the boundary."""
    boundary = signal.mean() if boundary == 'mean' else boundary
    signal = signal - boundary
    return np.where(np.diff(np.sign(signal)) != 0)[0]
