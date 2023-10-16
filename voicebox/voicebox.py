from abc import ABC, abstractmethod
from queue import Queue, Empty
from threading import Thread, Event
from typing import List, Optional

from voicebox.effects.dc_offset import RemoveDcOffset
from voicebox.effects.effect import Effect
from voicebox.effects.normalize import Normalize
from voicebox.sinks.sink import Sink
from voicebox.sinks.sounddevice import SoundDevice
from voicebox.tts.picotts import PicoTTS
from voicebox.tts.tts import TTS

Effects = List[Effect]


class BaseVoicebox(ABC):
    @abstractmethod
    def say(self, text: str) -> None:
        ...


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
            RemoveDcOffset(),
            Normalize(),
        ]

    @staticmethod
    def _default_sink() -> Sink:
        return SoundDevice()

    def say(self, text: str) -> None:
        audio = self.tts.get_speech(text)

        for effect in self.effects:
            audio = effect.apply(audio)

        self.sink.play(audio)


class VoiceboxThread(Thread, BaseVoicebox):
    """
    Allows messages to be queued and speech handled on a separate thread
    so the main thread is not blocked waiting for speech to complete.

    Example:
    ::
        voicebox = Voicebox(...)            # Build voicebox like normal
        voicebox = VoiceboxThread(voicebox) # Wrap voicebox in thread
        voicebox.start()                    # Start the voicebox thread
        voicebox.say('Hello, world!')       # Does not block; speech handled by thread
        voicebox.say('How are you?')        # Does not block
        # Do stuff in main thread while speech is happening...
    """

    voicebox: BaseVoicebox

    _say_queue: Queue
    _stop_event: Event

    def __init__(
            self,
            voicebox: BaseVoicebox,
            name: str = 'Voicebox',
            daemon: bool = True,
            **kwargs,
    ):
        """
        :param voicebox: The Voicebox instance that will be used to generate speech.
        :param name: Name of the thread.
        :param daemon: Whether the thread is daemonic (i.e. dies when the main thread exits).
        :param kwargs: Additional keyword args will get passed to the Thread constructor.
        """

        Thread.__init__(self, name=name, daemon=daemon, **kwargs)
        self.voicebox = voicebox

        self._say_queue = Queue()
        self._stop_event = Event()

    def say(self, text: str) -> None:
        """Add text to the queue of things to say."""
        self._say_queue.put(text)

    def stop(self, wait: bool = False, timeout: float = None) -> None:
        """Notify the thread to stop running."""

        self._stop_event.set()

        if wait:
            self.join(timeout=timeout)

    def wait_for_all_speech_to_complete(self) -> None:
        self._say_queue.join()

    def run(self):
        while not self._stop_event.is_set():
            if not (text := self._get_text()):
                continue

            try:
                self.voicebox.say(text)
            finally:
                self._say_queue.task_done()

    def _get_text(self) -> Optional[str]:
        try:
            return self._say_queue.get(timeout=1.)
        except Empty:
            return None
