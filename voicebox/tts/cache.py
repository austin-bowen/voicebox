from dataclasses import dataclass
from typing import Type, Union, Literal, Callable, Any, Mapping, Iterable

from cachetools import Cache, LRUCache

from voicebox.audio import Audio
from voicebox.tts import TTS
from voicebox.tts.utils import get_audio_from_wav_file
from voicebox.types import StrOrSSML, FileOrPath

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


@dataclass
class PrerecordedTTS(TTS):
    """
    Returns audio from a map of message texts to ``Audio`` instances.
    Useful for playing back pre-recorded messages. Also supports an
    optional fallback ``TTS`` instance for messages not in the map.
    """

    texts_to_audios: Mapping[StrOrSSML, Audio]
    """Mapping of message texts to ``Audio`` instances."""

    fallback_tts: TTS = None
    """
    Optional fallback ``TTS`` instance that will be used if a text is not found
    in ``messages``.
    """

    @classmethod
    def from_tts(
            cls,
            tts: TTS,
            texts: Iterable[StrOrSSML],
            use_as_fallback: bool = True,
    ) -> 'PrerecordedTTS':
        texts = {text: tts(text) for text in texts}
        return cls(texts, fallback_tts=tts if use_as_fallback else None)

    @classmethod
    def from_wav_files(
            cls,
            texts_to_files: Mapping[StrOrSSML, FileOrPath],
            fallback_tts: TTS = None
    ) -> 'PrerecordedTTS':
        messages = {
            text: get_audio_from_wav_file(file)
            for text, file in texts_to_files.values()
        }

        return cls(messages, fallback_tts=fallback_tts)

    def get_speech(self, text: StrOrSSML) -> Audio:
        try:
            return self.texts_to_audios[text]
        except KeyError:
            if self.fallback_tts is not None:
                return self.fallback_tts.get_speech(text)
            else:
                raise
