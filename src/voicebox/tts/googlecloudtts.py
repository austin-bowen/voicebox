from dataclasses import dataclass, field
from io import BytesIO

from google.api_core import gapic_v1
from google.cloud.texttospeech import (
    AudioConfig,
    AudioEncoding,
    SynthesisInput,
    TextToSpeechClient,
    VoiceSelectionParams,
)

from voicebox.audio import Audio
from voicebox.ssml import SSML
from voicebox.tts.tts import TTS
from voicebox.tts.utils import get_audio_from_wav_file
from voicebox.types import StrOrSSML


@dataclass
class GoogleCloudTTS(TTS):
    """
    TTS supplied by Google Cloud TTS.

    You will need to set up a Google Cloud project with billing enabled.
    See https://cloud.google.com/text-to-speech/docs/create-audio-text-client-libraries#client-libraries-usage-python
    """

    client: TextToSpeechClient
    voice_params: VoiceSelectionParams
    audio_config: AudioConfig = field(default_factory=AudioConfig)

    timeout: float = gapic_v1.method.DEFAULT

    def get_speech(self, text: StrOrSSML) -> Audio:
        self.audio_config.audio_encoding = AudioEncoding.LINEAR16

        input_ = (SynthesisInput(ssml=text) if isinstance(text, SSML) else
                  SynthesisInput(text=text))

        response = self.client.synthesize_speech(
            input=input_,
            voice=self.voice_params,
            audio_config=self.audio_config,
            timeout=self.timeout,
        )

        with BytesIO(response.audio_content) as wav_file:
            return get_audio_from_wav_file(wav_file)
