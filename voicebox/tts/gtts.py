from io import BytesIO

from gtts import gTTS as gTTS_
from pydub import AudioSegment

from voicebox.audio import Audio
from voicebox.tts.tts import TTS
from voicebox.tts.utils import get_audio_from_audio_segment
from voicebox.types import KWArgs, StrOrSSML


class gTTS(TTS):
    """
    Online TTS engine used by Google Translate.
    """

    gtts_kwargs: KWArgs

    def __init__(self, **gtts_kwargs: KWArgs):
        """
        :param gtts_kwargs: These will be passed to the ``gtts.gTTS`` constructor.
            See the docs for options: https://gtts.readthedocs.io/en/latest/module.html#module-gtts.tts
        """

        self.gtts_kwargs = gtts_kwargs

    def get_speech(self, text: StrOrSSML) -> Audio:
        gtts = gTTS_(text, **self.gtts_kwargs)

        mp3_file = BytesIO()
        gtts.write_to_fp(mp3_file)
        mp3_file.seek(0)

        audio_segment = AudioSegment.from_mp3(mp3_file)

        return get_audio_from_audio_segment(audio_segment)
