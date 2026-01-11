from pathlib import Path
from typing import Any, Iterator, Optional

from elevenlabs.client import ElevenLabs

from voicebox.tts import Mp3FileTTS
from voicebox.types import StrOrSSML


class ElevenLabsTTS(Mp3FileTTS):
    """
    TTS using the `ElevenLabs API <https://elevenlabs.io/>`_.

    Supports `SSML <https://www.w3.org/TR/speech-synthesis/>`_: ✔
    (`docs <https://elevenlabs.io/docs/speech-synthesis/prompting#pronunciation>`_)

    Args:
        voice_id:
            Voice to use. See `here <https://elevenlabs.io/docs/api-reference/get-voices>`_
            for a list of valid voice IDs.
        api_key:
            (Optional) Your ElevenLabs API key. If this and client are not given,
            then the client will pull the API key from the ``ELEVENLABS_API_KEY``
            env var. Note: Cannot be used with the ``client`` arg!
        client:
            (Optional) An :class:`elevenlabs.client.ElevenLabs` instance.
            Use this if you want to further customize the client behavior.
            Note: Cannot be used with the ``api_key`` arg!
        convert_kwargs:
            (Optional) Additional kwargs to pass to the ``client.text_to_speech.convert``
            call. See here for all options:
            https://elevenlabs.io/docs/api-reference/text-to-speech/convert
    """

    client: ElevenLabs
    voice_id: str
    convert_kwargs: Optional[dict[str, Any]]

    def __init__(
            self,
            *,
            voice_id: str,
            api_key: str = None,
            client: ElevenLabs = None,
            convert_kwargs: dict[str, Any] = None,
            temp_file_dir: str = None,
            temp_file_prefix: str = "voicebox-elevenlabs-",
    ):
        if api_key and client:
            raise ValueError("Cannot give both api_key and client args.")

        super().__init__(temp_file_dir, temp_file_prefix)

        self.voice_id = voice_id
        self.client = client or (ElevenLabs(api_key=api_key) if api_key else ElevenLabs())
        self.convert_kwargs = convert_kwargs or {}

    @property
    def api_key(self) -> str:
        # noinspection PyProtectedMember
        return self.client._client_wrapper._api_key

    def generate_speech_audio_file(self, text: StrOrSSML, audio_file_path: Path) -> None:
        mp3_data = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=text,
            **self.convert_kwargs,
        )

        with open(audio_file_path, "wb") as f:
            if isinstance(mp3_data, Iterator):
                for chunk in mp3_data:
                    f.write(chunk)
            else:
                f.write(mp3_data)
