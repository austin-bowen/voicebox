import subprocess
from dataclasses import dataclass, field
from typing import List

from voicebox.audio import Audio
from voicebox.ssml import SSML
from voicebox.tts.tts import TTS
from voicebox.tts.utils import get_audio_from_wav_file
from voicebox.types import StrOrSSML


@dataclass
class ESpeakConfig:
    amplitude: int = None
    word_gap_seconds: float = None
    # TODO -k
    line_length: int = None
    pitch: int = None
    speed: int = None
    voice: str = None
    no_final_pause: bool = False

    exe_path: str = 'espeak-ng'
    timeout: float = None


@dataclass
class ESpeakNG(TTS):
    """
    TTS with the eSpeak NG engine.

    You may need to install it, e.g. ``sudo apt install espeak-ng``.
    """

    config: ESpeakConfig = field(default_factory=ESpeakConfig)

    def get_speech(self, text: StrOrSSML) -> Audio:
        proc = self._get_proc(text)

        try:
            return get_audio_from_wav_file(proc.stdout)
        finally:
            proc.wait(timeout=self.config.timeout)

    def _get_proc(self, text: StrOrSSML):
        args = self._get_args(text)

        try:
            proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f'{e}; is espeak-ng installed? Try: sudo apt install espeak-ng'
            )

        proc.stdin.write(text.encode('utf-8'))
        proc.stdin.close()

        return proc

    def _get_args(self, text: StrOrSSML) -> List[str]:
        c = self.config

        args = [
            c.exe_path,
            '--stdin',  # Get input from stdin
            '-b', '1',  # Input text encoding UTF-8
            '--stdout',  # Write output to stdout
        ]

        if c.amplitude is not None:
            args.extend(('-a', str(c.amplitude)))

        if c.word_gap_seconds is not None:
            # Units of 10ms
            word_gap = round(c.word_gap_seconds * 100)
            args.extend(('-g', str(word_gap)))

        if c.line_length is not None:
            args.extend(('-l', str(c.line_length)))

        if c.pitch is not None:
            args.extend(('-p', str(c.pitch)))

        if c.speed is not None:
            args.extend(('-s', str(c.speed)))

        if c.voice is not None:
            args.extend(('-v', c.voice))

        if c.no_final_pause:
            args.append('-z')

        if isinstance(text, SSML):
            args.append('-m')

        return args
