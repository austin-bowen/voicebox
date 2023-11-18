from contextlib import closing
from dataclasses import dataclass
from typing import Literal, Sequence

import numpy as np
from mypy_boto3_polly.client import PollyClient
from mypy_boto3_polly.literals import LanguageCodeType, EngineType, VoiceIdType

from voicebox.audio import Audio
from voicebox.ssml import SSML
from voicebox.tts.tts import TTS
from voicebox.tts.utils import add_optional_items, get_audio_from_samples
from voicebox.types import StrOrSSML


@dataclass
class AmazonPolly(TTS):
    """
    TTS using Amazon Polly.

    See Amazon Polly documentation for full descriptions of the parameters:
    https://docs.aws.amazon.com/polly/latest/dg/API_SynthesizeSpeech.html
    """

    client: PollyClient
    """
    Boto3 Polly client, created by e.g.

    ``
    session = boto3.Session(...)
    client = session.client('polly')
    ``
    """

    voice_id: VoiceIdType
    """Voice ID to use for the synthesis."""

    engine: EngineType = None
    """
    Specifies the engine (``standard`` or ``neural``) for Amazon Polly to use
    when processing input text for speech synthesis.
    """

    language_code: LanguageCodeType = None
    """Optional language code for the Synthesize Speech request."""

    lexicon_names: Sequence[str] = None
    """
    List of one or more pronunciation lexicon names you want the service to
    apply during synthesis.
    """

    sample_rate: Literal[8000, 16000] = 16000

    def get_speech(self, text: StrOrSSML) -> Audio:
        kwargs = dict(
            OutputFormat='pcm',
            Text=text,
            VoiceId=self.voice_id,
            SampleRate=str(self.sample_rate),
            TextType='ssml' if isinstance(text, SSML) else 'text',
        )

        add_optional_items(kwargs, [
            ('Engine', self.engine),
            ('LanguageCode', self.language_code),
            ('LexiconNames', self.lexicon_names),
        ])

        response = self.client.synthesize_speech(**kwargs)

        with closing(response['AudioStream']) as audio_stream:
            signal_bytes = audio_stream.read()

        samples = np.frombuffer(signal_bytes, dtype=np.int16)

        return get_audio_from_samples(samples, self.sample_rate)
