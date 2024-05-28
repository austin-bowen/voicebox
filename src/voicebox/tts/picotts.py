import subprocess
from pathlib import Path

from voicebox.ssml import SSML
from voicebox.tts.tts import WavFileTTS
from voicebox.types import StrOrSSML


class PicoTTS(WavFileTTS):
    """
    TTS using `Pico TTS <https://www.openhab.org/addons/voice/picotts/>`_.

    You may need to install it:

    - On Debian/Ubuntu: ``sudo apt install libttspico-utils``

    Supports `SSML <https://www.w3.org/TR/speech-synthesis/>`_: ✘
    """

    pico2wave_path: str = 'pico2wave'
    language: str = None

    def __init__(
            self,
            pico2wave_path: str = 'pico2wave',
            language: str = None,
            temp_file_dir: str = None,
            temp_file_prefix: str = 'voicebox-pico-tts-',
    ):
        super().__init__(
            temp_file_dir=temp_file_dir,
            temp_file_prefix=temp_file_prefix,
        )

        self.pico2wave_path = pico2wave_path
        self.language = language

    def generate_speech_audio_file(self, text: StrOrSSML, file_path: Path) -> None:
        if isinstance(text, SSML):
            raise ValueError('PicoTTS does not support SSML.')

        args = [
            self.pico2wave_path,
            '-w', str(file_path),
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
