__all__ = [
    'Voicebox',
    'VoiceboxWithTextSplitter',
]

import asyncio
from abc import ABC, abstractmethod
from typing import Iterable

from voicebox.voiceboxes.splitter import Splitter, default_splitter


class Voicebox(ABC):
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


class VoiceboxWithTextSplitter(Voicebox):
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
