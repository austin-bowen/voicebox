from voicebox.effects.effect import Effect


class RemoveDcOffset(Effect):
    def apply(self, audio):
        audio.signal -= audio.signal.mean()
        return audio
