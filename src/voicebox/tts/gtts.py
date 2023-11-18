from io import BytesIO

from gtts import gTTS as gTTS_

from voicebox.audio import Audio
from voicebox.tts.tts import TTS
from voicebox.tts.utils import get_audio_from_mp3
from voicebox.types import KWArgs, StrOrSSML


class gTTS(TTS):
    """
    Online TTS engine used by Google Translate.
    """

    gtts_kwargs: KWArgs

    def __init__(self, **gtts_kwargs):
        """
        :param gtts_kwargs: These will be passed to the ``gtts.gTTS`` constructor.
            See the docs for options: https://gtts.readthedocs.io/en/latest/module.html#module-gtts.tts
        """

        self.gtts_kwargs = gtts_kwargs

    def get_speech(self, text: StrOrSSML) -> Audio:
        gtts = gTTS_(text, **self.gtts_kwargs)

        with BytesIO() as mp3_file:
            gtts.write_to_fp(mp3_file)
            mp3_file.seek(0)

            return get_audio_from_mp3(mp3_file)
