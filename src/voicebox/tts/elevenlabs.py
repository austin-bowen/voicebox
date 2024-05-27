from dataclasses import dataclass, field
from io import BytesIO
from typing import Union, Iterator

from elevenlabs import Voice, Model
from elevenlabs.client import ElevenLabs

from voicebox.audio import Audio
from voicebox.tts import TTS
from voicebox.tts.utils import get_audio_from_mp3, add_optional_items
from voicebox.types import StrOrSSML


@dataclass
class ElevenLabsTTS(TTS):
    """
    TTS using the `ElevenLabs API <https://elevenlabs.io/>`_.

    Supports `SSML <https://www.w3.org/TR/speech-synthesis/>`_: ✔
    (`docs <https://elevenlabs.io/docs/speech-synthesis/prompting#pronunciation>`_)

    Args:
        client:
            An optional :class:`elevenlabs.client.ElevenLabs` instance.
            Use this if you have an API key you wish to use. See
            `here <https://github.com/elevenlabs/elevenlabs-python?tab=readme-ov-file#client-instantiation>`_
            for simple client instantiation example.
        voice:
            Optional voice to use. Can be an :class:`elevenlabs.Voice` instance,
            or a string representing the voice ID. See
            `here <https://elevenlabs.io/docs/api-reference/get-voices>`_ for
            a list of valid voice IDs. If not given, the default voice is used.
        model:
            Optional model to use. Can be an :class:`elevenlabs.Model` instance,
            or a string representing the model ID. See
            `here <https://elevenlabs.io/docs/api-reference/get-models>`_ for
            a list of valid model IDs. If not given, the default model is used.
    """

    client: ElevenLabs = field(default_factory=ElevenLabs)
    voice: Union[str, Voice] = None
    model: Union[str, Model] = None

    def get_speech(self, text: StrOrSSML) -> Audio:
        mp3_data = self.client.generate(**self._get_generate_args(text))

        if isinstance(mp3_data, Iterator):
            mp3_data = b"".join(mp3_data)

        with BytesIO(mp3_data) as mp3_data:
            return get_audio_from_mp3(mp3_data)

    def _get_generate_args(self, text: StrOrSSML) -> dict:
        return add_optional_items(
            dict(text=text),
            [
                ('voice', self.voice),
                ('model', self.model),
            ]
        )
