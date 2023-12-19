__all__ = [
    'PedalboardEffect',
    'pedalboard_effects',
]

from dataclasses import dataclass
from typing import Sequence

import pedalboard

from voicebox.audio import Audio
from voicebox.effects.effect import Effect


@dataclass
class PedalboardEffect(Effect):
    """
    Wrapper around Pedalboard library plugins from Spotify.

    See the Pedalboard library documentation for the full list of plugins:
    https://spotify.github.io/pedalboard/reference/pedalboard.html

    Example:
        >>> from voicebox.effects import PedalboardEffect
        >>> import pedalboard
        >>> effects = [
        >>>     ...,
        >>>     PedalboardEffect(pedalboard.Reverb()),
        >>> ]
    """

    plugin: pedalboard.Plugin

    def apply(self, audio: Audio) -> Audio:
        audio.signal = self.plugin.process(audio.signal, audio.sample_rate, reset=True)
        return audio


def pedalboard_effects(
        *effects: pedalboard.Plugin,
) -> Sequence[PedalboardEffect]:
    """
    Creates a sequence of PedalboardEffect objects from Pedalboard plugins.

    Example:
        >>> from voicebox.effects import pedalboard_effects
        >>> import pedalboard
        >>> effects = pedalboard_effects(
        >>>     pedalboard.Distortion(),
        >>>     pedalboard.Reverb(),
        >>> )
    """

    return [PedalboardEffect(plugin) for plugin in effects]
