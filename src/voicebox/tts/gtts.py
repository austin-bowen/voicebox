from pathlib import Path
from typing import Any

from gtts import gTTS as gTTS_

from voicebox.ssml import SSML
from voicebox.tts.tts import Mp3FileTTS
from voicebox.types import KWArgs, StrOrSSML


class gTTS(Mp3FileTTS):
    """
    Online TTS using the `gTTS <https://gtts.readthedocs.io>`_
    library, which queries the Google Translate TTS API under the hood.

    Supports `SSML <https://www.w3.org/TR/speech-synthesis/>`_: ✘

    Args:
        gtts_kwargs:
            These will be passed to the :class:`gtts.gTTS` constructor.
            See the `gTTS docs
            <https://gtts.readthedocs.io/en/latest/module.html#module-gtts.tts>`_
            for options.
    """

    gtts_kwargs: KWArgs

    def __init__(
            self,
            temp_file_dir: str = None,
            temp_file_prefix: str = 'voicebox-gtts-',
            **gtts_kwargs: dict[str, Any],
    ):
        super().__init__(temp_file_dir, temp_file_prefix)
        self.gtts_kwargs = gtts_kwargs

    def generate_speech_audio_file(self, text: StrOrSSML, audio_file_path: Path) -> None:
        if isinstance(text, SSML):
            raise ValueError('gTTS does not support SSML.')

        gtts = gTTS_(text, **self.gtts_kwargs)

        with open(audio_file_path, 'wb') as mp3_file:
            gtts.write_to_fp(mp3_file)
