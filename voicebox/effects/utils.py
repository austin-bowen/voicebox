import numpy as np


def get_crossover_points(signal: np.ndarray, boundary: float = 'mean') -> np.ndarray:
    """Returns the indices of the points just before the signal crosses the boundary."""
    boundary = signal.mean() if boundary == 'mean' else boundary
    signal = signal - boundary
    return np.where(np.diff(np.sign(signal)) != 0)[0]
