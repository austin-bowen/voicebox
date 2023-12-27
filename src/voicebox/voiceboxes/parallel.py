__all__ = ['ParallelVoicebox']

from abc import abstractmethod
from dataclasses import dataclass
from queue import Queue, Empty
from threading import Thread, Event
from typing import TypeVar, Iterable

from voicebox.audio import Audio
from voicebox.effects import Effects, default_effects
from voicebox.sinks import Sink, default_sink
from voicebox.tts import TTS, default_tts
from voicebox.types import StrOrSSML
from voicebox.voiceboxes.base import BaseVoicebox

T = TypeVar('T')


class _QueueThread(Thread):
    queue_get_timeout: float

    _queue: Queue
    _stop_event: Event

    def __init__(
            self,
            start: bool = True,
            queue_max_size: int = 0,
            queue_get_timeout: float = 1.,
            **kwargs,
    ):
        super().__init__(**kwargs)

        self.queue_get_timeout = queue_get_timeout

        self._queue = Queue(queue_max_size)
        self._stop_event = Event()

        if start:
            self.start()

    def put(self, item: T) -> None:
        self._queue.put(item)

    def stop(self, wait: bool = False, timeout: float = None) -> None:
        """Notify the thread to stop running."""

        self._stop_event.set()

        if wait:
            self.join(timeout=timeout)

    def wait_until_done(self) -> None:
        """Wait until the queue is empty."""
        self._queue.join()

    def run(self):
        for item in self._get_items():
            try:
                self._process_item(item)
            finally:
                self._queue.task_done()

    def _get_items(self) -> Iterable[T]:
        while not self._stop_event.is_set():
            try:
                yield self._queue.get(timeout=self.queue_get_timeout)
            except Empty:
                continue

    @abstractmethod
    def _process_item(self, item: T) -> None:
        ...


class _SinkQueueThread(_QueueThread):
    sink: Sink

    def __init__(self, sink: Sink, **kwargs):
        self.sink = sink
        super().__init__(**kwargs)

    def _process_item(self, audio: Audio) -> None:
        self.sink.play(audio)


class _TTSAndEffectsQueueThread(_QueueThread):
    tts: TTS
    effects: Effects
    sink_queue_thread: _SinkQueueThread

    def __init__(
            self,
            tts: TTS,
            effects: Effects,
            sink_queue_thread: _SinkQueueThread,
            **kwargs,
    ):
        self.tts = tts
        self.effects = effects
        self.sink_queue_thread = sink_queue_thread
        super().__init__(**kwargs)

    def _process_item(self, text: StrOrSSML) -> None:
        audio = self.tts.get_speech(text)

        for effect in self.effects:
            audio = effect.apply(audio)

        self.sink_queue_thread.put(audio)


@dataclass
class ParallelVoicebox(BaseVoicebox):
    """
    Handles speech on a separate thread so the main thread is not blocked
    waiting for speech to complete.

    Also eliminates loading time between messages by loading the audio for the
    next message while the current message is playing.

    Note: This is not meant to be instantiated directly.
    Use :meth:`ParallelVoicebox.build` instead.

    Example:
        >>> voicebox = ParallelVoicebox.build(...)
        >>> voicebox.say('Hello, world!')   # Does not block; speech handled by thread
        >>> voicebox.say('How are you?')    # Does not block
        >>> # Do stuff in main thread while speech is happening...
        >>> voicebox.wait_until_done()      # Call before program end to prevent cutoff
        >>>
        >>> # Can be used as context manager
        >>> with ParallelVoicebox.build(...) as voicebox:
        >>>     ...
        >>> # Voicebox threads are stopped after exiting `with` block
    """

    _tts_and_effects_queue_thread: _TTSAndEffectsQueueThread
    _sink_queue_thread: _SinkQueueThread

    @classmethod
    def build(
            cls,
            tts: TTS = None,
            effects: Effects = None,
            sink: Sink = None,
            start: bool = True,
            queue_get_timeout: float = 1.,
            daemon: bool = True,
    ):
        """
        Args:
            tts:
                The :class:`voicebox.tts.TTS` engine to use.
            effects:
                Sequence of :class:`voicebox.effects.Effect` instances to apply to
                the audio before playing it.
            sink:
                The :class:`voicebox.sinks.Sink` to use to play the audio.
            start:
                Whether to start the threads.
            queue_get_timeout:
                Seconds to wait for text to appear in the queue of things to say
                between checks of the stop flag.
            daemon:
                Whether the thread is daemonic (i.e. dies when the main thread exits).
        """

        tts = tts or default_tts()
        effects = effects or default_effects()
        sink = sink or default_sink()

        sink_queue_thread = _SinkQueueThread(
            sink,
            queue_max_size=1,
            queue_get_timeout=queue_get_timeout,
            start=start,
            daemon=daemon,
        )

        tts_and_effects_queue_thread = _TTSAndEffectsQueueThread(
            tts=tts,
            effects=effects,
            sink_queue_thread=sink_queue_thread,
            queue_get_timeout=queue_get_timeout,
            start=start,
            daemon=daemon,
        )

        return cls(tts_and_effects_queue_thread, sink_queue_thread)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def say(self, text: str) -> None:
        self._tts_and_effects_queue_thread.put(text)

    def start(self) -> None:
        """Start the threads."""
        self._tts_and_effects_queue_thread.start()
        self._sink_queue_thread.start()

    def is_alive(self) -> bool:
        """Returns ``True`` iff all the threads are alive."""

        return (
            self._tts_and_effects_queue_thread.is_alive()
            and self._sink_queue_thread.is_alive()
        )

    def join(self, timeout: float = None) -> None:
        """
        Wait for running threads to stop.

        Args:
            timeout:
                Wait up to this many seconds. ``None`` waits forever.

        :param timeout:
        :return:
        """

        self._tts_and_effects_queue_thread.join(timeout=timeout)
        self._sink_queue_thread.join(timeout=timeout)

    def stop(self, wait: bool = False, timeout: float = None) -> None:
        """
        Stop the running threads.

        Args:
            wait:
                Whether to wait for the threads to stop.
            timeout:
                If waiting, then wait up to this many seconds.
                ``None`` waits forever.
        """

        self._tts_and_effects_queue_thread.stop(wait=wait, timeout=timeout)
        self._sink_queue_thread.stop(wait=wait, timeout=timeout)

    def wait_until_done(self) -> None:
        """
        Waits until all speech is done.

        Useful to run before program end to prevent speech from being cut off.
        """

        self._tts_and_effects_queue_thread.wait_until_done()
        self._sink_queue_thread.wait_until_done()
