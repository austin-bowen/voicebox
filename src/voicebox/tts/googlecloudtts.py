import wave
from dataclasses import dataclass, field
from io import BytesIO

import numpy as np
from google.api_core import gapic_v1
from google.cloud.texttospeech import (
    AudioConfig,
    AudioEncoding,
    SynthesisInput,
    TextToSpeechClient,
    VoiceSelectionParams,
)

from voicebox.audio import Audio
from voicebox.tts.tts import TTS
from voicebox.types import StrOrSSML
from voicebox.ssml import SSML


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

        response = self.client.synthesize_speech(
            input=SynthesisInput(ssml=text) if isinstance(text, SSML) else SynthesisInput(text=text),
            voice=self.voice_params,
            audio_config=self.audio_config,
            timeout=self.timeout,
        )

        with BytesIO(response.audio_content) as wav_data:
            with wave.open(wav_data, 'rb') as wav_file:
                signal_bytes = wav_file.readframes(-1)
                sample_rate = wav_file.getframerate()

        signal = np.frombuffer(signal_bytes, dtype=np.int16)

        # Scale to [-1, 1]
        bits_per_sample = 16
        max_value = 2 ** (bits_per_sample - 1) - 1
        signal = signal.astype(float) / max_value
        signal = signal.astype(np.float32)

        return Audio(signal, sample_rate)
