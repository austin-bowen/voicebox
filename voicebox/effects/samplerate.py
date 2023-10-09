from dataclasses import dataclass
from typing import Callable

from voicebox.audio import Audio
from voicebox.effects.effect import Effect


@dataclass
class ChangeSampleRate(Effect):
    modifier: Callable[[int], int]

    def apply(self, audio: Audio) -> Audio:
        audio.sample_rate = self.modifier(audio.sample_rate)
        return audio
