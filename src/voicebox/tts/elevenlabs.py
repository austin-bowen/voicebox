from typing import Any, Iterator

import numpy as np
from elevenlabs.client import ElevenLabs

from voicebox.audio import Audio
from voicebox.tts import TTS
from voicebox.tts.utils import get_audio_from_samples
from voicebox.types import StrOrSSML


class ElevenLabsTTS(TTS):
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
        sample_rate:
            (Optional) PCM audio sample rate. Defaults to 32kHz.
            This is used to set the ``output_format`` of the request.
            See `here <https://elevenlabs.io/docs/api-reference/text-to-speech/convert#request.query.output_format>`_
            for valid options. Note: You must pick a sample rate from one of the
            ``output_format`` options beginning with ``pcm_``! Other codecs are
            not supported.
        convert_kwargs:
            (Optional) Additional kwargs to pass to the ``client.text_to_speech.convert``
            call. See here for all options:
            https://elevenlabs.io/docs/api-reference/text-to-speech/convert
    """

    client: ElevenLabs
    voice_id: str
    sample_rate: int
    convert_kwargs: dict[str, Any]

    def __init__(
            self,
            *,
            voice_id: str,
            api_key: str = None,
            client: ElevenLabs = None,
            sample_rate: int = 32_000,
            convert_kwargs: dict[str, Any] = None,
    ):
        if api_key and client:
            raise ValueError("Cannot give both api_key and client args.")

        self.voice_id = voice_id
        self.client = client or (ElevenLabs(api_key=api_key) if api_key else ElevenLabs())
        self.sample_rate = sample_rate
        self.convert_kwargs = convert_kwargs or {}

    @property
    def api_key(self) -> str:
        # noinspection PyProtectedMember
        return self.client._client_wrapper._api_key

    @property
    def output_format(self):
        return f"pcm_{self.sample_rate}"

    def get_speech(self, text: StrOrSSML) -> Audio:
        pcm_data = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=text,
            output_format=self.output_format,
            **self.convert_kwargs,
        )

        if isinstance(pcm_data, Iterator):
            pcm_data = b"".join(pcm_data)

        pcm_data = np.frombuffer(
            pcm_data,
            # Little-endian, signed int, 2 bytes per int
            dtype="<i2",
        )

        return get_audio_from_samples(pcm_data, self.sample_rate)
