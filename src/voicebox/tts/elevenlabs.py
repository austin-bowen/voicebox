from dataclasses import dataclass, field
from io import BytesIO
from typing import Union

import elevenlabs
from elevenlabs import Voice, Model

from voicebox.audio import Audio
from voicebox.tts import TTS
from voicebox.tts.utils import get_audio_from_mp3
from voicebox.types import StrOrSSML


@dataclass
class ElevenLabs(TTS):
    """
    TTS using the `ElevenLabs API <https://elevenlabs.io/>`_.

    Supports `SSML <https://www.w3.org/TR/speech-synthesis/>`_: ✔
    (`docs <https://elevenlabs.io/docs/speech-synthesis/prompting#pronunciation>`_)

    Args:
        api_key:
            Optional API key to use. Not needed if already set via
            :func:`elevenlabs.set_api_key()` or env var ``ELEVEN_API_KEY``.
        voice:
            Optional voice to use. Can be an :class:`elevenlabs.Voice` instance,
            or a string representing the voice ID. See
            `here <https://elevenlabs.io/docs/api-reference/get-voices>`_ for
            a list of valid voice IDs. If not given, a default voice is used.
        model:
            Optional model to use. Can be an :class:`elevenlabs.Model` instance,
            or a string representing the model ID. See
            `here <https://elevenlabs.io/docs/api-reference/get-models>`_ for
            a list of valid model IDs. If not given, a default model is used.
    """

    api_key: str = None
    voice: Union[str, Voice] = field(default_factory=lambda: elevenlabs.DEFAULT_VOICE)
    model: Union[str, Model] = 'eleven_monolingual_v1'

    def get_speech(self, text: StrOrSSML) -> Audio:
        mp3_data = elevenlabs.generate(
            text,
            api_key=self.api_key,
            voice=self.voice,
            model=self.model,
        )

        with BytesIO(mp3_data) as mp3_data:
            return get_audio_from_mp3(mp3_data)
