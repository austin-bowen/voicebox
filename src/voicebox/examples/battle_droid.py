"""
Voicebox emulating the OOM-9 command battle droid from Star Wars: Episode I.

Requires the Google Cloud TTS engine.
"""

from google.cloud.texttospeech import TextToSpeechClient, VoiceSelectionParams, AudioConfig

from voicebox.effects import Vocoder, Normalize, RingMod
from voicebox.effects.effect import Effects
from voicebox.examples.demo import demo
from voicebox.tts import GoogleCloudTTS
from voicebox.tts.tts import TTS


def build_battle_droid_tts(client: TextToSpeechClient = None) -> TTS:
    if not client:
        client = TextToSpeechClient()

    return GoogleCloudTTS(
        client=client,
        voice_params=VoiceSelectionParams(
            language_code='en-US',
            name='en-US-Standard-D',
        ),
        audio_config=AudioConfig(
            speaking_rate=1.,
            pitch=0.0,
        ),
    )


def build_battle_droid_effects() -> Effects:
    vocoder = Vocoder.build(
        carrier_freq=92,
        min_freq=100,
        max_freq=10000,
        bands=40,
        bandwidth=0.5,
    )

    return [
        vocoder,
        RingMod(carrier_freq=40, dry=.75, wet=.25),
        Normalize(),
    ]


if __name__ == '__main__':
    demo(
        description=__doc__,
        tts=build_battle_droid_tts(),
        effects=build_battle_droid_effects(),
        default_messages=[
            'Roger roger.',
            "Yes Viceroy. If they're down here sir, we'll find them.",
            "Viceroy, we have captured the queen.",
            "My troops are in position to start searching the swamps for these rumored "
            "underwater villages. They will not stay hidden for long.",
        ],
    )
