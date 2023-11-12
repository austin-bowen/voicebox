from dataclasses import dataclass

import pedalboard

from voicebox.audio import Audio
from voicebox.effects.effect import Effect

__all__ = ['PedalboardEffect']


@dataclass
class PedalboardEffect(Effect):
    """
    Wrapper around Pedalboard library plugins from Spotify.

    See the Pedalboard library documentation for the full list of plugins:
    https://spotify.github.io/pedalboard/reference/pedalboard.html

    Example:
    ::
        from voicebox.effects import PedalboardEffect
        import pedalboard
        voicebox.effects.append(
            PedalboardEffect(pedalboard.Reverb())
        )
    """

    plugin: pedalboard.Plugin

    def apply(self, audio: Audio) -> Audio:
        audio.signal = self.plugin.process(audio.signal, audio.sample_rate, reset=True)
        return audio
