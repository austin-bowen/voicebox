__all__ = ['reliable_tts']

from typing import Union, Iterable, Literal

from voicebox.tts import CachedTTS, TTS, FallbackTTS, RetryTTS, default_tts
from voicebox.tts.cache import Size, SizeFunc


def reliable_tts(
        ttss: Union[TTS, Iterable[TTS]] = None,
        retry_max_attempts: int = 3,
        cache_max_size: Size = 60,
        cache_size_func: Union[Literal['bytes', 'count', 'seconds'], SizeFunc] = 'seconds',
) -> TTS:
    """
    Takes zero or more TTS instances and returns a single TTS that will attempt
    to use each TTS in the order given, up to ``retry_max_attempts`` times
    each, until one succeeds. Outputs will also be cached to speed up retrieval
    of repeated phrases.

    This is useful if e.g. you have an online TTS that is subject to network
    failures, which the retries may alleviate, and you want to fall back to an
    offline TTS in the event that the online TTS fails all attempts.

    If no TTS instance is provided, then a default TTS instance will be used.
    """

    if ttss is None:
        ttss = [default_tts()]
    elif isinstance(ttss, TTS):
        ttss = [ttss]

    ttss = [RetryTTS(tts, max_attempts=retry_max_attempts) for tts in ttss]

    ttss = [CachedTTS.build(
        tts,
        max_size=cache_max_size,
        size_func=cache_size_func,
    ) for tts in ttss]

    ttss = FallbackTTS(ttss)

    return ttss
