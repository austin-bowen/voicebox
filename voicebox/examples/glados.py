"""
Voicebox emulating GLaDOS from the Portal video game series developed by Valve.
"""

from dataclasses import dataclass, field
from random import Random

import numpy as np

from voicebox import Voicebox
from voicebox.effects import Vocoder, RemoveDcOffset, Normalize
from voicebox.effects.vocoder import sawtooth_wave
from voicebox.tts import gTTS
from voicebox.voicebox import Effects


def build_glados_voicebox() -> Voicebox:
    return Voicebox(
        tts=gTTS(),
        effects=build_glados_effects(),
    )


def build_glados_effects() -> Effects:
    carrier_wave = RandomSemitoneSawtoothWave(
        min_freq=160.,
        max_semitones=6,
        pitch_duration=0.3,
    )

    vocoder = Vocoder.build(
        carrier_wave=carrier_wave,
        min_freq=100,
        max_freq=10000,
        bands=40,
        bandwidth=0.5,
    )

    return [
        vocoder,
        RemoveDcOffset(),
        Normalize(),
    ]


@dataclass
class RandomSemitoneSawtoothWave:
    min_freq: float
    max_semitones: int
    pitch_duration: float

    rng: Random = field(default_factory=Random)

    def __call__(self, times: np.ndarray) -> np.ndarray:
        dt = times[1] - times[0]
        chunk_size = round(self.pitch_duration / dt)

        out = np.zeros_like(times)
        for i in range(0, len(times), chunk_size):
            semitones = self.rng.randint(0, self.max_semitones)
            f = self.min_freq * 2 ** (semitones / 12)
            time_chunk = times[i:i + chunk_size]
            radians = 2 * np.pi * f * time_chunk
            out[i:i + chunk_size] = sawtooth_wave(radians)

        return out


def main():
    glados = build_glados_voicebox()

    glados.say_all([
        'Hello and, again, welcome to the Aperture Science computer-aided enrichment center.',
        'We hope your brief detention in the relaxation vault has been a pleasant one.',
        'Your specimen has been processed and we are now ready to begin the test proper.',
        'Before we start, however, keep in mind that although fun and learning are the primary goals '
        'of all enrichment center activities, serious injuries may occur.',
    ])


if __name__ == '__main__':
    main()