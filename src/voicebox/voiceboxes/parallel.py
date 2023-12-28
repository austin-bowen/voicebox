__all__ = ['ParallelVoicebox']

from abc import abstractmethod
from queue import Empty
from threading import Thread, Event
from typing import TypeVar, Iterable

from voicebox.audio import Audio
from voicebox.effects import Effects, default_effects
from voicebox.sinks import Sink, default_sink
from voicebox.tts import TTS, default_tts
from voicebox.types import StrOrSSML
from voicebox.voiceboxes.base import VoiceboxWithTextSplitter
from voicebox.voiceboxes.queue import Queue
from voicebox.voiceboxes.splitter import Splitter

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

    def wait_until_done(self, timeout: float = None) -> None:
        """Wait until the queue is empty."""
        self._queue.join(timeout=timeout)

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
        ...  # pragma: no cover


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


class ParallelVoicebox(VoiceboxWithTextSplitter):
    """
    Handles speech on a separate thread so the main thread is not blocked
    waiting for speech to complete.

    Also eliminates loading time between messages by loading the audio for the
    next message while the current message is playing.

    Example:
        >>> voicebox = ParallelVoicebox(...)
        >>> voicebox.say('Hello, world!')   # Does not block; speech handled by thread
        >>> voicebox.say('How are you?')    # Does not block
        >>> # Do stuff in main thread while speech is happening...
        >>> voicebox.wait_until_done()      # Call before program end to prevent cutoff
        >>>
        >>> # Can be used as context manager
        >>> with ParallelVoicebox(...) as voicebox:
        >>>     ...
        >>> # Voicebox threads are stopped after exiting `with` block

    Args:
        tts:
            The :class:`voicebox.tts.TTS` engine to use.
        effects:
            Sequence of :class:`voicebox.effects.Effect` instances to apply to
            the audio before playing it.
        sink:
            The :class:`voicebox.sinks.Sink` to use to play the audio.
        text_splitter:
            The :class:`voicebox.voiceboxes.splitter.Splitter` to use to split
            the text into chunks to be spoken. Defaults to no splitting.
        start:
            Whether to start the threads.
        queue_get_timeout:
            Seconds to wait for text to appear in the queue of things to say
            between checks of the stop flag.
        daemon:
            Whether the thread is daemonic (i.e. dies when the main thread exits).
    """

    _tts_and_effects_queue_thread: _TTSAndEffectsQueueThread
    _sink_queue_thread: _SinkQueueThread

    def __init__(
            self,
            tts: TTS = None,
            effects: Effects = None,
            sink: Sink = None,
            text_splitter: Splitter = None,
            start: bool = True,
            queue_get_timeout: float = 1.,
            daemon: bool = True,
    ):
        super().__init__(text_splitter)

        tts = tts if tts is not None else default_tts()
        effects = effects if effects is not None else default_effects()
        sink = sink if sink is not None else default_sink()

        self._sink_queue_thread = _SinkQueueThread(
            sink,
            queue_max_size=1,
            queue_get_timeout=queue_get_timeout,
            start=start,
            daemon=daemon,
        )

        self._tts_and_effects_queue_thread = _TTSAndEffectsQueueThread(
            tts=tts,
            effects=effects,
            sink_queue_thread=self._sink_queue_thread,
            queue_get_timeout=queue_get_timeout,
            start=start,
            daemon=daemon,
        )

    @property
    def tts(self) -> TTS:
        return self._tts_and_effects_queue_thread.tts

    @tts.setter
    def tts(self, tts: TTS) -> None:
        self._tts_and_effects_queue_thread.tts = tts

    @property
    def effects(self) -> Effects:
        return self._tts_and_effects_queue_thread.effects

    @effects.setter
    def effects(self, effects: Effects) -> None:
        self._tts_and_effects_queue_thread.effects = effects

    @property
    def sink(self) -> Sink:
        return self._sink_queue_thread.sink

    @sink.setter
    def sink(self, sink: Sink) -> None:
        self._sink_queue_thread.sink = sink

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def _say_chunk(self, chunk: str) -> None:
        self._tts_and_effects_queue_thread.put(chunk)

    def start(self) -> None:
        """Start the threads."""
        self._tts_and_effects_queue_thread.start()
        self._sink_queue_thread.start()

    def is_alive(self) -> bool:
        """Return whether the threads are alive."""

        return (
                self._tts_and_effects_queue_thread.is_alive()
                and self._sink_queue_thread.is_alive()
        )

    def join(self, timeout: float = None) -> None:
        """
        Wait until the threads terminate.

        Args:
            timeout:
                Wait up to this many seconds. ``None`` waits forever.
        """

        self._tts_and_effects_queue_thread.join(timeout=timeout)
        self._sink_queue_thread.join(timeout=timeout)

    def stop(self, wait: bool = False, timeout: float = None) -> None:
        """
        Notify the threads to stop running.

        Args:
            wait:
                Whether to wait for the threads to stop.
            timeout:
                If waiting, then wait up to this many seconds.
                ``None`` waits forever.
        """

        self._tts_and_effects_queue_thread.stop(wait=wait, timeout=timeout)
        self._sink_queue_thread.stop(wait=wait, timeout=timeout)

    def wait_until_done(self, timeout: float = None) -> None:
        """
        Wait until all speech is done.

        Useful to run before program end to prevent speech from being cut off.

        Raises:
            NotFinished:
                If ``timeout`` is not ``None`` and the timeout is reached
                before all speech is done.
        """

        self._tts_and_effects_queue_thread.wait_until_done(timeout=timeout)
        self._sink_queue_thread.wait_until_done(timeout=timeout)
