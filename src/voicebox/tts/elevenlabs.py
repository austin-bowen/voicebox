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
    api_key: str = None
    """
    Optional API key to use. Not needed if already set via
    ``elevenlabs.set_api_key()`` or env var ``ELEVEN_API_KEY``.
    """

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
