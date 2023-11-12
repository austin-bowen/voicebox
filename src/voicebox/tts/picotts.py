import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from voicebox.audio import Audio
from voicebox.tts.tts import TTS
from voicebox.tts.utils import get_audio_from_wav_file
from voicebox.types import StrOrSSML


@dataclass
class PicoTTS(TTS):
    """
    TSS supplied by Pico TTS.

    You may need to install this with your system's package manager.
    On Debian/Ubuntu: ``sudo apt install libttspico-utils``
    """

    pico2wave_path: str = 'pico2wave'
    language: str = None

    temp_wav_file_prefix: str = 'voicebox-pico-tts-'
    temp_wav_file_dir: str = None

    def get_speech(self, text: StrOrSSML) -> Audio:
        with tempfile.NamedTemporaryFile(
                prefix=self.temp_wav_file_prefix,
                suffix='.wav',
                dir=self.temp_wav_file_dir,
                delete=True,
        ) as wav_file:
            wav_path = Path(wav_file.name)
            self._generate_speech_wav_file(text, wav_path)
            return get_audio_from_wav_file(wav_path)

    def _generate_speech_wav_file(self, text: str, wav_path: Path) -> None:
        args = [
            self.pico2wave_path,
            '-w', str(wav_path),
        ]

        if self.language is not None:
            args.extend(('-l', self.language))

        args.append(text)

        try:
            subprocess.run(args, check=True)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f'{e}; is PicoTTS installed? Try: sudo apt install libttspico-utils'
            )
