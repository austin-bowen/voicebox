from io import BytesIO
from typing import Any

import requests

from voicebox.audio import Audio
from voicebox.tts import TTS
from voicebox.tts.utils import add_optional_items, get_audio_from_wav_file
from voicebox.types import StrOrSSML

DEFAULT_VOICE_AI_API_URL: str = "https://dev.voice.ai/api/v1/tts/speech"


class VoiceAiTTS(TTS):
    """
    TTS using the `Voice.AI API <https://voice.ai/docs/api-reference/text-to-speech/generate-speech>`_.

    Supports `SSML <https://www.w3.org/TR/speech-synthesis/>`_: ✔
    (`docs <https://elevenlabs.io/docs/speech-synthesis/prompting#pronunciation>`_)

    Args:
        api_key:
            Your Voice.AI API key. Create one here: https://voice.ai/app/dashboard/developers
        voice_id:
            (Optional) Voice ID. If omitted, the default built-in voice is used.
        temperature:
            (Optional) Temperature for generation (0.0-2.0).
        top_p:
            (Optional) Top-p sampling parameter (0.0-1.0).
        model:
            (Optional) TTS model to use. See here for options:
            https://voice.ai/docs/api-reference/text-to-speech/generate-speech#body-model-one-of-0
        language:
            (Optional) Language code (ISO 639-1 format, e.g., 'en', 'es', 'fr').
            Defaults to 'en' if not provided.
        api_url:
            (Optional) Override the default API URL.
        extra_json:
            (Optional) Extra request parameters to put in the JSON payload.
        extra_headers:
            (Optional) Extra headers to add to the request.
        request_kwargs:
            (Optional) Extra kwargs to pass to the ``requests.post()`` call.
    """

    def __init__(
        self,
        api_key: str,
        voice_id: str = None,
        temperature: float = None,
        top_p: float = None,
        model: str = None,
        language: str = None,
        api_url: str = DEFAULT_VOICE_AI_API_URL,
        extra_json: dict[str, Any] = None,
        extra_headers: dict[str, str] = None,
        request_kwargs: dict[str, Any] = None,
    ):
        self.api_key = api_key

        self.voice_id = voice_id
        self.temperature = temperature
        self.top_p = top_p
        self.model = model
        self.language = language
        self.api_url = api_url
        self.extra_json = extra_json or {}
        self.extra_headers = extra_headers or {}
        self.request_kwargs = request_kwargs or {}

    def get_speech(self, text: StrOrSSML) -> Audio:
        response = requests.post(
            self.api_url,
            headers=self._build_headers(),
            json=self._build_json(text),
            **self.request_kwargs,
        )

        response.raise_for_status()

        with BytesIO(response.content) as wav_file:
            return get_audio_from_wav_file(wav_file)

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers,
        }

    def _build_json(self, text: StrOrSSML) -> dict[str, Any]:
        json = {
            "text": text,
            "audio_format": "wav",
        }

        add_optional_items(
            json,
            [
                ("voice_id", self.voice_id),
                ("temperature", self.temperature),
                ("top_p", self.top_p),
                ("model", self.model),
                ("language", self.language),
            ],
        )

        json.update(self.extra_json)

        return json
