from dataclasses import dataclass
from typing import List

from voicebox.effects.effect import Effect
from voicebox.sinks.sink import Sink
from voicebox.tts.tts import TTS


@dataclass
class Voicebox:
    tts: TTS
    effects: List[Effect]
    sink: Sink

    def speak(self, text: str) -> None:
        audio = self.tts.get_speech(text)

        for effect in self.effects:
            audio = effect.apply(audio)

        self.sink.play(audio)
