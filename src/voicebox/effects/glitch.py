__all__ = ['Glitch']

from dataclasses import dataclass, field
from random import Random

import numpy as np

from voicebox.audio import Audio
from voicebox.effects.effect import Effect


@dataclass
class Glitch(Effect):
    """
    Creates a glitchy sound by randomly repeating small chunks of audio.

    Args:
        chunk_time:
            Length of each repeated chunk, in seconds.
        p_repeat:
            Probability of repeating each chunk.
        max_repeats:
            Maximum number of times to repeat each chunk.
        rng:
            Random number generator to use.
            One will be constructed if not given.
    """

    chunk_time: float = 0.1
    p_repeat: float = 0.07
    max_repeats: int = 3

    rng: Random = field(default_factory=Random)

    def apply(self, audio: Audio) -> Audio:
        chunk_size = round(self.chunk_time * audio.sample_rate)

        new_signal = []
        for i in range(0, len(audio.signal), chunk_size):
            chunk = audio.signal[i:i + chunk_size]
            new_signal.append(chunk)

            if self.rng.random() < self.p_repeat:
                chunk -= chunk.mean()  # Removing DC offset helps reduce popping effect

                for _ in range(self.rng.randint(1, self.max_repeats)):
                    new_signal.append(chunk)

        audio.signal = np.concatenate(new_signal)

        return audio
