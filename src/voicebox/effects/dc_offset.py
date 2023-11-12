from voicebox.effects.effect import Effect

__all__ = ['RemoveDcOffset']


class RemoveDcOffset(Effect):
    def apply(self, audio):
        audio.signal -= audio.signal.mean()
        return audio
