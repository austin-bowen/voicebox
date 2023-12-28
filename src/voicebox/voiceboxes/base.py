__all__ = [
    'BaseVoicebox',
    'VoiceboxWithTextSplitter',
    'Voicebox',
]

import asyncio
from abc import ABC, abstractmethod
from typing import Iterable

from voicebox.audio import Audio
from voicebox.effects import SeriesChain, default_effects
from voicebox.effects.effect import Effects
from voicebox.sinks import default_sink
from voicebox.sinks.sink import Sink
from voicebox.tts import default_tts
from voicebox.tts.tts import TTS
from voicebox.voiceboxes.splitter import Splitter, default_splitter


class BaseVoicebox(ABC):
    """Base class of all voiceboxes."""

    @abstractmethod
    def say(self, text: str) -> None:
        """Say the given text."""
        ...  # pragma: no cover

    async def say_async(self, text: str, loop=None, executor=None) -> None:
        """Say the given text asynchronously."""
        loop = loop or asyncio.get_running_loop()
        await loop.run_in_executor(executor, self.say, text)

    def say_all(self, texts: Iterable[str]) -> None:
        """Say all the given texts, in order."""
        for text in texts:
            self.say(text)

    async def say_all_async(
            self,
            texts: Iterable[str],
            loop=None,
            executor=None,
    ) -> None:
        """Say all the given texts, in order, asynchronously."""
        loop = loop or asyncio.get_running_loop()
        await loop.run_in_executor(executor, self.say_all, texts)


class VoiceboxWithTextSplitter(BaseVoicebox):
    """Base class of all voiceboxes that use a text splitter."""

    text_splitter: Splitter

    def __init__(self, text_splitter: Splitter = None):
        self.text_splitter = text_splitter or default_splitter()

    def say(self, text: str) -> None:
        """Say the given text."""
        for chunk in self.text_splitter.split(text):
            self._say_chunk(chunk)

    @abstractmethod
    def _say_chunk(self, chunk: str) -> None:
        """Say the given chunk of text."""
        ...  # pragma: no cover


class Voicebox(VoiceboxWithTextSplitter):
    """
    Uses a TTS engine to convert text to audio, applies a series of effects
    to the audio, and then plays the audio.

    Args:
        tts:
            The :class:`voicebox.tts.TTS` engine to use.
        effects:
            Sequence of :class:`voicebox.effects.Effect` instances to apply to
            the audio before playing it.
        sink:
            The :class:`voicebox.sinks.Sink` to use to play the audio.
        text_splitter:
            The :class:`voicebox.voiceboxes.splitter.Splitter` to use to split
            the text into chunks to be spoken. Defaults to no splitting.
    """

    tts: TTS
    effects: Effects
    sink: Sink

    def __init__(
            self,
            tts: TTS = None,
            effects: Effects = None,
            sink: Sink = None,
            text_splitter: Splitter = None,
    ):
        super().__init__(text_splitter)

        self.tts = tts if tts is not None else default_tts()
        self.effects = effects if effects is not None else default_effects()
        self.sink = sink if sink is not None else default_sink()

    def _say_chunk(self, chunk: str) -> None:
        audio = self._get_tts_audio_with_effects(chunk)
        self.sink.play(audio)

    def _get_tts_audio_with_effects(self, text: str) -> Audio:
        audio = self.tts.get_speech(text)

        effects_chain = SeriesChain(*self.effects)
        audio = effects_chain(audio)

        return audio
