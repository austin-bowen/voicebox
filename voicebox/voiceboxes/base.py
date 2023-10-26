from abc import ABC, abstractmethod
from typing import Iterable

from voicebox.audio import Audio
from voicebox.effects import SeriesChain
from voicebox.effects.effect import Effects
from voicebox.effects.normalize import Normalize
from voicebox.sinks.sink import Sink
from voicebox.sinks.sounddevice import SoundDevice
from voicebox.tts.picotts import PicoTTS
from voicebox.tts.tts import TTS

__all__ = ['BaseVoicebox', 'Voicebox']


class BaseVoicebox(ABC):
    @abstractmethod
    def say(self, text: str) -> None:
        ...

    def say_all(self, texts: Iterable[str]) -> None:
        for text in texts:
            self.say(text)


class Voicebox(BaseVoicebox):
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
            Normalize(),
        ]

    @staticmethod
    def _default_sink() -> Sink:
        return SoundDevice()

    def say(self, text: str) -> None:
        audio = self._get_tts_audio_with_effects(text)
        self.sink(audio)

    def _get_tts_audio_with_effects(self, text: str) -> Audio:
        audio = self.tts.get_speech(text)

        effects_chain = SeriesChain(*self.effects)
        audio = effects_chain(audio)

        return audio
