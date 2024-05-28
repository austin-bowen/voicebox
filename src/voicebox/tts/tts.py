import logging
from tempfile import NamedTemporaryFile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import Sequence, Type, Tuple, Optional

from voicebox.audio import Audio
from voicebox.tts.utils import get_audio_from_mp3, get_audio_from_wav_file
from voicebox.types import StrOrSSML

log = logging.getLogger(__name__)


class TTS(ABC):
    """Base class for text-to-speech engines."""

    def __call__(self, text: StrOrSSML) -> Audio:
        return self.get_speech(text)

    @abstractmethod
    def get_speech(self, text: StrOrSSML) -> Audio:
        """Returns audio of the given text."""
        ...  # pragma: no cover


class AudioFileTTS(TTS):
    """Base class for text-to-speech engines that generate audio files."""

    temp_file_dir: Optional[str]
    temp_file_prefix: str
    temp_file_type: str

    def __init__(
            self,
            temp_file_dir: Optional[str],
            temp_file_prefix: str,
            temp_file_type: str,
    ):
        self.temp_file_dir = temp_file_dir
        self.temp_file_prefix = temp_file_prefix
        self.temp_file_type = temp_file_type

    def get_speech(self, text: StrOrSSML) -> Audio:
        with NamedTemporaryFile(
                prefix=self.temp_file_prefix,
                suffix=f'.{self.temp_file_type}',
                dir=self.temp_file_dir,
                delete=True,
        ) as audio_file:
            audio_file_path = Path(audio_file.name)
            self.generate_speech_audio_file(text, audio_file_path)
            # TODO: Use audio_file instead?
            return self._get_audio_from_file(audio_file_path)

    @abstractmethod
    def generate_speech_audio_file(self, text: StrOrSSML, audio_file_path: Path) -> None:
        """Generates a speech audio file from the given text."""
        ...

    def _get_audio_from_file(self, audio_file_path: Path) -> Audio:
        if self.temp_file_type == 'wav':
            return get_audio_from_wav_file(audio_file_path)
        elif self.temp_file_type == 'mp3':
            return get_audio_from_mp3(audio_file_path)
        else:
            raise ValueError(f'Unsupported temp_file_type: {self.temp_file_type}')


@dataclass
class FallbackTTS(TTS):
    """
    Attempts to call the TTSs in order, returning results from the first TTS
    that does not raise an exception.

    Useful if you have e.g. an online TTS that you want to use primarily,
    and want to fall back to an offline TTS in case something goes wrong.

    Args:
        ttss:
            The TTSs to try, in order.
        exceptions_to_catch:
            The exceptions to catch and log when calling the TTSs.
            If an exception is raised that is not in this tuple,
            then it will not be caught.
        log:
            The logger to use for logging exceptions.
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

    Args:
        tts:
            The TTS to call.
        max_attempts:
            The maximum number of attempts to make.
        exceptions_to_catch:
            The exceptions to catch and log when calling the TTS.
            If an exception is raised that is not in this tuple,
            then it will not be caught.
        log:
            The logger to use for logging exceptions.
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
