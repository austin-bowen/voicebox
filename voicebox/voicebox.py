from typing import List

from voicebox.effects.dc_offset import RemoveDcOffset
from voicebox.effects.effect import Effect
from voicebox.effects.normalize import Normalize
from voicebox.sinks.sink import Sink
from voicebox.sinks.sounddevice import SoundDevice
from voicebox.tts.picotts import PicoTTS
from voicebox.tts.tts import TTS

Effects = List[Effect]


class Voicebox:
    tts: TTS
    effects: Effects
    sink: Sink

    def __init__(self, tts: TTS = None, effects: Effects = None, sink: Sink = None):
        self.tts = tts if tts is not None else self._default_tts()
        self.effects = effects if effects is not None else self._default_effects()
        self.sink = sink if sink is not None else self._default_sink()

    @staticmethod
    def _default_tts() -> TTS:
        return PicoTTS()

    @staticmethod
    def _default_effects() -> Effects:
        return [
            RemoveDcOffset(),
            Normalize(),
        ]

    @staticmethod
    def _default_sink() -> Sink:
        return SoundDevice()

    def say(self, text: str) -> None:
        audio = self.tts.get_speech(text)

        for effect in self.effects:
            audio = effect.apply(audio)

        self.sink.play(audio)
