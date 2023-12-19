from voicebox.effects.effect import Effect

__all__ = ['RemoveDcOffset']


class RemoveDcOffset(Effect):
    """Removes any DC offset from the audio signal by subtracting the mean."""

    def apply(self, audio):
        audio.signal -= audio.signal.mean()
        return audio
