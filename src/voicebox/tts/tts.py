import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import Logger
from typing import Sequence, Type, Tuple

from voicebox.audio import Audio
from voicebox.types import StrOrSSML

log = logging.getLogger(__name__)


class TTS(ABC):
    def __call__(self, text: StrOrSSML) -> Audio:
        return self.get_speech(text)

    @abstractmethod
    def get_speech(self, text: StrOrSSML) -> Audio:
        ...


@dataclass
class FallbackTTS(TTS):
    """
    Useful if you have e.g. an online TTS that you want to use primarily,
    and want to fall back to an offline TTS in case something goes wrong.

    Attempts to call the TTSs in order, returning results from the first TTS
    that does not raise an exception.
    """

    ttss: Sequence[TTS]

    exceptions_to_catch: Tuple[Type[BaseException]] = (Exception,)
    log: Logger = log

    def get_speech(self, text: StrOrSSML) -> Audio:
        for i, tts in enumerate(self.ttss):
            try:
                return tts.get_speech(text)
            except BaseException as e:
                self.handle_exception(e, tts, i)

                is_last = i + 1 >= len(self.ttss)
                should_catch = isinstance(e, self.exceptions_to_catch)
                if is_last or not should_catch:
                    raise

        raise ValueError('self.ttss is empty')

    def handle_exception(self, e: BaseException, tts: TTS, tts_index: int) -> None:
        message = f'Exception occurred calling TTS={tts} (index {tts_index})'
        self.log.exception(message, exc_info=e)


@dataclass
class RetryTTS(TTS):
    """
    If an exception occurs while getting speech from the given TTS,
    retry until ``max_attempts`` is reached.
    """

    tts: TTS
    max_attempts: int = 3

    exceptions_to_catch: Tuple[Type[BaseException]] = (Exception,)
    log: Logger = log

    def get_speech(self, text: StrOrSSML) -> Audio:
        for attempt in range(1, self.max_attempts + 1):
            try:
                return self.tts.get_speech(text)
            except BaseException as e:
                self.handle_exception(e, attempt)

                is_last_attempt = attempt >= self.max_attempts
                should_catch = isinstance(e, self.exceptions_to_catch)
                if is_last_attempt or not should_catch:
                    raise

        raise ValueError(f'self.max_attempts must be > 0; '
                         f'max_attempts={self.max_attempts}')

    def handle_exception(self, e: BaseException, attempt: int) -> None:
        message = f'TTS attempt {attempt}/{self.max_attempts} failed'
        self.log.exception(message, exc_info=e)
