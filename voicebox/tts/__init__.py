from voicebox.tts.espeakng import ESpeakConfig, ESpeakNG

try:
    from voicebox.tts.googlecloudtts import GoogleCloudTTS
except ImportError:
    pass

from voicebox.tts.picotts import PicoTTS
