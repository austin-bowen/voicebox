"""
Voicebox emulating 343 Guilty Spark from the Halo video game series
developed by Bungee and 343 Industries.

Requires the Google Cloud TTS engine.
"""

from google.cloud.texttospeech import TextToSpeechClient, VoiceSelectionParams, AudioConfig

from voicebox.effects import Normalize, Flanger
from voicebox.effects.effect import Effects
from voicebox.examples.demo import demo
from voicebox.tts import GoogleCloudTTS
from voicebox.tts.tts import TTS


def build_spark_tts(client: TextToSpeechClient = None) -> TTS:
    if not client:
        client = TextToSpeechClient()

    return GoogleCloudTTS(
        client=client,
        voice_params=VoiceSelectionParams(
            language_code='en-US',
            name='en-US-Polyglot-1',
        ),
        audio_config=AudioConfig(
            speaking_rate=1.2,
            pitch=8.,
        ),
    )


def build_spark_effects() -> Effects:
    return [
        Flanger(),
        Normalize(),
    ]


if __name__ == '__main__':
    demo(
        description=__doc__,
        tts=build_spark_tts(),
        effects=build_spark_effects(),
        default_messages=[
            'Greetings. I am the Monitor of Installation zero 4. I am 3 4 3, Guilty Spark.',
            'Someone has released The Flood. '
            'My function is to prevent it from leaving this Installation. But I require your assistance.'
        ],
    )
