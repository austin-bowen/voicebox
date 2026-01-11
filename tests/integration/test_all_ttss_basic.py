from typing import Type
import os

import boto3
from google.cloud.texttospeech import TextToSpeechClient, VoiceSelectionParams
from parameterized import parameterized
from dotenv import load_dotenv

from voicebox.tts import *

TTS_CLASSES = (
    AmazonPolly,
    ElevenLabsTTS,
    ESpeakNG,
    GoogleCloudTTS,
    gTTS,
    ParlerTTS,
    PicoTTS,
    Pyttsx3TTS,
    VoiceAiTTS,
)


def get_speech_name_func(testcase_func, param_num, param) -> str:
    test_name = testcase_func.__name__
    tts_class_name = param.args[0].__name__
    return f'{test_name}({tts_class_name})'


@parameterized.expand(TTS_CLASSES, name_func=get_speech_name_func)
def test_get_speech(tts_class: Type[TTS]):
    load_dotenv()

    if tts_class is AmazonPolly:
        session = boto3.Session(region_name='us-east-1', profile_name='polly')
        client = session.client('polly')
        tts = AmazonPolly(client=client, voice_id='Aditi')

    elif tts_class is GoogleCloudTTS:
        tts = GoogleCloudTTS(
            client=TextToSpeechClient(),
            voice_params=VoiceSelectionParams(language_code='en-US'),
        )

    elif tts_class is ParlerTTS:
        tts = ParlerTTS.build()

    elif tts_class is VoiceAiTTS:
        api_key = os.getenv("VOICE_AI_API_KEY")
        tts = VoiceAiTTS(api_key)

    else:
        tts = tts_class()

    audio = tts.get_speech('Hello, world!')
    audio.check()
