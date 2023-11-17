from queue import Queue, Empty
from threading import Thread, Event
from typing import Optional

from voicebox.voiceboxes.base import BaseVoicebox

__all__ = ['VoiceboxThread']


class VoiceboxThread(Thread, BaseVoicebox):
    """
    Allows messages to be queued and speech handled on a separate thread
    so the main thread is not blocked waiting for speech to complete.

    Example:
    ::
        voicebox = Voicebox(...)            # Build voicebox like normal
        voicebox = VoiceboxThread(voicebox) # Wrap voicebox in thread
        voicebox.say('Hello, world!')       # Does not block; speech handled by thread
        voicebox.say('How are you?')        # Does not block
        # Do stuff in main thread while speech is happening...
    """

    voicebox: BaseVoicebox
    queue_get_timeout: float

    _say_queue: Queue
    _stop_event: Event

    def __init__(
            self,
            voicebox: BaseVoicebox,
            start: bool = True,
            queue_get_timeout: float = 1.,
            name: str = 'Voicebox',
            daemon: bool = True,
    ):
        """
        :param voicebox: The Voicebox instance that will be used to generate speech.
        :param start: If ``True``, go ahead and start the thread.
        :param queue_get_timeout: How long to wait for text to appear in the queue
            of things to say between checks of the stop flag.
        :param name: Name of the thread.
        :param daemon: Whether the thread is daemonic (i.e. dies when the main thread exits).
        """

        Thread.__init__(self, name=name, daemon=daemon)

        self.voicebox = voicebox
        self.queue_get_timeout = queue_get_timeout

        self._say_queue = Queue()
        self._stop_event = Event()

        if start:
            self.start()

    def say(self, text: str) -> None:
        """Add text to the queue of things to say."""
        self._say_queue.put(text)

    def stop(self, wait: bool = False, timeout: float = None) -> None:
        """Notify the thread to stop running."""

        self._stop_event.set()

        if wait:
            self.join(timeout=timeout)

    def wait_until_done(self) -> None:
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
            return self._say_queue.get(timeout=self.queue_get_timeout)
        except Empty:
            return None
