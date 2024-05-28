from pathlib import Path

import pyttsx3
from pyttsx3 import Engine

from voicebox.tts.tts import WavFileTTS
from voicebox.types import StrOrSSML


class Pyttsx3TTS(WavFileTTS):
    """
    TTS using `pyttsx3 <https://pyttsx3.readthedocs.io/>`_.

    Args:
        engine:
            (Optional) The `pyttsx3` engine to use. If not given, a new engine
            will be created via `pyttsx3.init()`.
        temp_file_dir:
            (Optional) The directory to save temporary audio files to. If not
            given, then the default temporary directory will be used.
        temp_file_prefix:
            (Optional) The prefix to use for temporary audio files.
            Defaults to 'voicebox-pyttsx3-'.
    """

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
