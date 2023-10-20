"""
Voicebox emulating 343 Guilty Spark from the Halo video game series
developed by Bungee and 343 Industries.

Requires the Google Cloud TTS engine.
"""

from google.cloud.texttospeech import TextToSpeechClient, VoiceSelectionParams, AudioConfig

from voicebox import Voicebox
from voicebox.effects import RemoveDcOffset, Normalize, Flanger
from voicebox.tts import GoogleCloudTTS
from voicebox.tts.tts import TTS
from voicebox.voicebox import Effects


def build_spark_voicebox(gctts_client: TextToSpeechClient = None) -> Voicebox:
    return Voicebox(
        tts=build_spark_tts(gctts_client),
        effects=build_spark_effects(),
    )


def build_spark_tts(client: TextToSpeechClient) -> TTS:
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
        RemoveDcOffset(),
        Normalize(),
    ]


def main():
    import sys

    spark = build_spark_voicebox()

    messages = [sys.argv[1]] if len(sys.argv) > 1 else [
        'Greetings. I am the Monitor of Installation zero 4. I am 3 4 3, Guilty Spark.',
        'Someone has released The Flood. '
        'My function is to prevent it from leaving this Installation. But I require your assistance.'
    ]

    spark.say_all(messages)


if __name__ == '__main__':
    main()
