import subprocess
from dataclasses import dataclass
from pathlib import Path

from voicebox.tts.tts import TTS
from voicebox.tts.utils import get_audio_from_wav_file
from voicebox.types import Audio


@dataclass
class PicoTTS(TTS):
    """
    TSS supplied by Pico TTS.

    You may need to install this with your system's package manager.
    On Debian/Ubuntu: ``sudo apt install libttspico-utils``
    """

    pico2wave_path: str = 'pico2wave'
    language: str = 'en-US'

    def get_speech(self, text: str) -> Audio:
        audio_path = self._generate_speech_wav_file(text)

        try:
            return get_audio_from_wav_file(audio_path)
        finally:
            audio_path.unlink()

    def _generate_speech_wav_file(self, text: str) -> Path:
        # TODO use tempfile
        wav_path = Path('temp.wav')

        subprocess.run(
            [
                self.pico2wave_path,
                '-w', str(wav_path),
                '-l', self.language,
                text,
            ],
            check=True,
        )

        return wav_path
