from dataclasses import dataclass

import numpy as np


@dataclass
class Audio:
    signal: np.ndarray
    sample_rate: int
