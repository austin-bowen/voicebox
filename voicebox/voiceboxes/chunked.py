import re
from abc import ABC, abstractmethod
from queue import Queue
from threading import Thread
from typing import Iterable, Callable, TypeVar, Any

from voicebox.audio import Audio
from voicebox.sinks.sink import Sink
from voicebox.ssml import SSML
from voicebox.tts import TTS
from voicebox.voiceboxes.base import Voicebox
from voicebox.effects.effect import Effects

__all__ = [
    'ChunkedVoicebox',
    'ParallelChunkedVoicebox',
    'Splitter',
    'DelimiterSplitter',
    'SentenceSplitter',
]

T = TypeVar('T')
V = TypeVar('V')


class Splitter(ABC):
    """Splits text into chunks."""

    @abstractmethod
    def split(self, text: str) -> Iterable[str]:
        ...


class DelimiterSplitter(Splitter):
    """Splits text on delimiter characters."""

    _delimiters: str
    _delimiter_pattern: re.Pattern

    def __init__(self, delimiters: str):
        self.delimiters = delimiters

    @property
    def delimiters(self) -> str:
        return self._delimiters

    @delimiters.setter
    def delimiters(self, delimiters: str) -> None:
        self._delimiters = delimiters
        self._delimiter_pattern = re.compile(rf'([{delimiters}]+)')

    def split(self, text: str) -> Iterable[str]:
        # Do not split SSML
        if isinstance(text, SSML):
            return text

        result = self._delimiter_pattern.split(text)
        result = zip(result[0::2], result[1::2])
        result = (''.join(pair).strip() for pair in result)
        return result


class SentenceSplitter(DelimiterSplitter):
    """Splits text on sentence delimiters '.', '!', and '?'."""

    def __init__(self):
        super().__init__(delimiters='.!?')


class ChunkedVoicebox(Voicebox):
    """
    Decreases time-to-speech by splitting the message text into chunks
    (sentences by default) and saying each chunk individually.
    """

    splitter: Splitter

    def __init__(
            self,
            tts: TTS = None,
            effects: Effects = None,
            sink: Sink = None,
            splitter: Splitter = None,
    ):
        super().__init__(tts, effects, sink)
        self.splitter = splitter if splitter is not None else self._default_splitter()

    @staticmethod
    def _default_splitter() -> Splitter:
        return SentenceSplitter()

    def say(self, text: str) -> None:
        text_chunks = self._get_text_chunks(text)
        audio_chunks = self._get_audio_chunks(text_chunks)

        for audio in audio_chunks:
            self.sink.play(audio)

    def _get_text_chunks(self, text: str) -> Iterable[str]:
        return self.splitter.split(text)

    def _get_audio_chunks(self, text_chunks: Iterable[str]) -> Iterable[Audio]:
        map_func = self._get_map_func()
        return map_func(self._get_tts_audio_with_effects, text_chunks)

    def _get_map_func(self):
        return map


class ParallelChunkedVoicebox(ChunkedVoicebox):
    """
    Decreases time-to-speech by splitting the message text into chunks
    (sentences by default) and saying each chunk individually. While one chunk
    of audio is being spoken, the next chunk is prepared in parallel.
    """

    queue_size: int

    def __init__(
            self,
            tts: TTS = None,
            effects: Effects = None,
            sink: Sink = None,
            splitter: Splitter = None,
            queue_size: int = 1,
    ):
        super().__init__(tts, effects, sink, splitter)
        self.queue_size = queue_size

    def _get_map_func(self):
        return _MapThread(queue_size=self.queue_size).map


class _MapThread(Thread):
    """Performs a ``map(func, items)`` in a parallel thread."""

    _func: Callable[[T], V]
    _items: Iterable[T]
    _queue: Queue
    _done_sentinel: Any

    def __init__(
            self,
            queue_size: int = 0,
            done_sentinel: Any = object(),
            name: str = '_MapThread',
            daemon: bool = True,
    ):
        super().__init__(name=name, daemon=daemon)

        self._queue = Queue(maxsize=queue_size)
        self._done_sentinel = done_sentinel

    def map(self, func: Callable[[T], V], items: Iterable[T]) -> Iterable[V]:
        self._func = func
        self._items = items

        self.start()

        while (item := self._queue.get()) is not self._done_sentinel:
            yield item

    def run(self):
        try:
            for result in map(self._func, self._items):
                self._queue.put(result)
        finally:
            self._queue.put(self._done_sentinel)
