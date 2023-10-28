import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Iterable, Callable, TypeVar, Any, Union, Dict

import nltk.tokenize
from nltk.tokenize.api import TokenizerI

from voicebox.audio import Audio
from voicebox.effects.effect import Effects
from voicebox.sinks.sink import Sink
from voicebox.ssml import SSML
from voicebox.tts import TTS
from voicebox.voiceboxes.base import Voicebox

__all__ = [
    'ChunkedVoicebox',
    'ParallelChunkedVoicebox',
    'Splitter',
    'RegexSplitter',
    'SimpleSentenceSplitter',
]

T = TypeVar('T')
V = TypeVar('V')


class Splitter(ABC):
    """Splits text into chunks."""

    @abstractmethod
    def split(self, text: str) -> Iterable[str]:
        ...


class RegexSplitter(Splitter):
    """Splits text on regex pattern."""

    pattern: re.Pattern
    join_split_group: bool

    def __init__(self, pattern: Union[str, re.Pattern], join_split_group: bool = True):
        self.pattern = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        self.join_split_group = join_split_group

    def split(self, text: str) -> Iterable[str]:
        # Do not split SSML
        if isinstance(text, SSML):
            return text

        result = self.pattern.split(text)
        result = map(str.strip, result)
        result = filter(bool, result)

        if self.join_split_group:
            result = list(result)
            pairs = zip(result[0::2], result[1::2])
            result = (''.join(pair) for pair in pairs)

        return result


class SimpleSentenceSplitter(RegexSplitter):
    """Splits text on sentence punctuation '.', '!', and '?'."""

    def __init__(self):
        super().__init__(r'([.!?]+\s+|$)')


@dataclass
class NltkTokenizerSplitter(Splitter):
    """Uses an NLTK tokenizer to split text."""

    tokenizer: TokenizerI

    def split(self, text: str) -> Iterable[str]:
        return self.tokenizer.tokenize(text)


class PunktSentenceSplitter(NltkTokenizerSplitter):
    """
    Uses the Punkt sentence tokenizer from NLTK to split text into sentences
    more intelligently than a simple pattern-based splitter. It can handle
    instances of mid-sentence punctuation very well; e.g. "Mr. Jones went to
    see Dr. Sherman" would be correctly split into only one sentence.

    Requires that the Punkt NLTK resource be located on disk, e.g. by downloading via:

    >>> import nltk; nltk.download('punkt')

    If the resource does not exist when an instance of this class is created,
    and ``download`` is set to ``True``, then this class will attempt to
    download the resource automatically using the above method.
    """

    def __init__(
            self,
            language: str = 'english',
            download: bool = False,
            download_kwargs: Dict[str, Any] = None,
            load_kwargs: Dict[str, Any] = None,
    ):
        tokenizer = self._download_and_load_tokenizer(language, download, download_kwargs, load_kwargs)
        super().__init__(tokenizer)

    def _download_and_load_tokenizer(
            self,
            language: str = 'english',
            download: bool = False,
            download_kwargs: Dict[str, Any] = None,
            load_kwargs: Dict[str, Any] = None,
    ) -> TokenizerI:
        try:
            return self._load_tokenizer(language, load_kwargs)
        except LookupError:
            if download:
                nltk.download('punkt', **(download_kwargs or {}))
                return self._load_tokenizer(language, load_kwargs)
            else:
                raise LookupError('You can fix this error by setting the constructor arg `download=True`.')

    def _load_tokenizer(self, language: str, load_kwargs: Dict[str, Any] = None) -> TokenizerI:
        return nltk.data.load(
            self._get_punkt_resource_url(language),
            **(load_kwargs or {}),
        )

    def _get_punkt_resource_url(self, language: str) -> str:
        return f'tokenizers/punkt/{language}.pickle'


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
        return SimpleSentenceSplitter()

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
