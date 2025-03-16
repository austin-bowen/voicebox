from pathlib import Path
from typing import Iterator, Union

from elevenlabs import Model, Voice
from elevenlabs.client import ElevenLabs

from voicebox.tts import Mp3FileTTS
from voicebox.tts.utils import add_optional_items
from voicebox.types import StrOrSSML


class ElevenLabsTTS(Mp3FileTTS):
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

    client: ElevenLabs
    voice: Union[str, Voice, None]
    model: Union[str, Model, None]

    def __init__(
            self,
            client: ElevenLabs = None,
            voice: Union[str, Voice] = None,
            model: Union[str, Model] = None,
            temp_file_dir: str = None,
            temp_file_prefix: str = 'voicebox-elevenlabs-',
    ):
        super().__init__(temp_file_dir, temp_file_prefix)
        self.client = client or ElevenLabs()
        self.voice = voice
        self.model = model

    def generate_speech_audio_file(self, text: StrOrSSML, audio_file_path: Path) -> None:
        mp3_data = self.client.generate(**self._get_generate_args(text))

        with open(audio_file_path, 'wb') as f:
            if isinstance(mp3_data, Iterator):
                for chunk in mp3_data:
                    f.write(chunk)
            else:
                f.write(mp3_data)

    def _get_generate_args(self, text: StrOrSSML) -> dict:
        return add_optional_items(
            dict(text=text),
            [
                ('voice', self.voice),
                ('model', self.model),
            ]
        )
