from pathlib import Path

import pyttsx3
from pyttsx3 import Engine

from voicebox.tts.tts import WavFileTTS
from voicebox.types import StrOrSSML


class Pyttsx3TTS(WavFileTTS):
    def __init__(
            self,
            engine: Engine = None,
            temp_file_dir: str = None,
            temp_file_prefix: str = 'voicebox-pyttsx3-',
    ):
        super().__init__(
            temp_file_dir=temp_file_dir,
            temp_file_prefix=temp_file_prefix,
        )

        self.engine = engine if engine is not None else pyttsx3.init()

    def generate_speech_audio_file(self, text: StrOrSSML, file_path: Path) -> None:
        self.engine.save_to_file(text, str(file_path))
        self.engine.runAndWait()
