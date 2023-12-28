__all__ = ['SimpleVoicebox']

from voicebox.audio import Audio
from voicebox.effects import Effects, default_effects, SeriesChain
from voicebox.sinks import Sink, default_sink
from voicebox.tts import TTS, default_tts
from voicebox.voiceboxes.base import VoiceboxWithTextSplitter
from voicebox.voiceboxes.splitter import Splitter


class SimpleVoicebox(VoiceboxWithTextSplitter):
    """
    Uses a TTS engine to convert text to audio, applies a series of effects
    to the audio, and then plays the audio.

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
    """

    tts: TTS
    effects: Effects
    sink: Sink

    def __init__(
            self,
            tts: TTS = None,
            effects: Effects = None,
            sink: Sink = None,
            text_splitter: Splitter = None,
    ):
        super().__init__(text_splitter)

        self.tts = tts if tts is not None else default_tts()
        self.effects = effects if effects is not None else default_effects()
        self.sink = sink if sink is not None else default_sink()

    def _say_chunk(self, chunk: str) -> None:
        audio = self._get_tts_audio_with_effects(chunk)
        self.sink.play(audio)

    def _get_tts_audio_with_effects(self, text: str) -> Audio:
        audio = self.tts.get_speech(text)

        effects_chain = SeriesChain(*self.effects)
        audio = effects_chain(audio)

        return audio
