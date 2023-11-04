from dataclasses import dataclass
from typing import Type, Union, Literal, Callable, Any

from cachetools import Cache, LRUCache

from voicebox.audio import Audio
from voicebox.tts import TTS
from voicebox.types import StrOrSSML

Size = Union[int, float]

SizeFunc = Callable[[Any], Size]
"""Returns the size of the given item."""


@dataclass
class CachedTTS(TTS):
    """Wraps a ``TTS`` instance in a cache to reduce calls to the ``TTS``."""

    tts: TTS
    cache: Cache

    @staticmethod
    def build(
            tts: TTS,
            max_size: Size = 60,
            size_func: Union[Literal['bytes', 'count', 'seconds'], SizeFunc] = 'seconds',
            cache_class: Type[Cache] = LRUCache,
    ) -> 'CachedTTS':
        """
        Constructs a cache that by default will keep the most recently used
        60 seconds of audio, and wraps the given ``TTS`` instance in the cache
        so the ``TTS`` is only called for text not contained in the cache.

        Args:
            tts: The TTS instance to wrap. Will be called for text not
                contained in the cache.
            max_size: The maximum size of the cache, as determined by
                ``size_func``. Defaults to 60 (seconds).
            size_func: The function that measures the size of each item.
                If set to 'seconds' (default), then ``max_size`` will be in
                units of audio seconds. If set to 'bytes', then ``max_size``
                will be in units of audio bytes. If set to 'count', then
                ``max_size`` will be simply the number of audio clips to cache.
                Alternatively, any function that takes an ``Audio`` instance
                as input and returns a size value can be passed in.
            cache_class: The ``Cache`` class used to construct the cache.
                Defaults to ``cachetools.LRUCache``, a Least Recently Used
                cache.

        Returns:
            An instance of ``CachedTTS``.
        """

        if size_func == 'bytes':
            size_func = lambda audio: audio.len_bytes
        elif size_func == 'count':
            size_func = lambda audio: 1
        elif size_func == 'seconds':
            size_func = lambda audio: audio.len_seconds

        cache = cache_class(maxsize=max_size, getsizeof=size_func)

        return CachedTTS(tts, cache)

    def get_speech(self, text: StrOrSSML) -> Audio:
        try:
            return self.cache[text]
        except KeyError:
            audio = self.tts.get_speech(text)
            return self._add_to_cache(text, audio)

    def _add_to_cache(self, text: StrOrSSML, audio: Audio) -> Audio:
        try:
            self.cache[text] = audio
        except ValueError as e:
            if str(e) != 'value too large':
                raise

        return audio
