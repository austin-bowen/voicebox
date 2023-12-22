from io import BytesIO

from gtts import gTTS as gTTS_

from voicebox.audio import Audio
from voicebox.ssml import SSML
from voicebox.tts.tts import TTS
from voicebox.tts.utils import get_audio_from_mp3
from voicebox.types import KWArgs, StrOrSSML


class gTTS(TTS):
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

    def __init__(self, **gtts_kwargs):
        self.gtts_kwargs = gtts_kwargs

    def get_speech(self, text: StrOrSSML) -> Audio:
        if isinstance(text, SSML):
            raise ValueError('gTTS does not support SSML.')

        gtts = gTTS_(text, **self.gtts_kwargs)

        with BytesIO() as mp3_file:
            gtts.write_to_fp(mp3_file)
            mp3_file.seek(0)

            return get_audio_from_mp3(mp3_file)
