from voicebox.tts.tts import TTS, FallbackTTS, RetryTTS

try:
    from voicebox.tts.amazonpolly import AmazonPolly
except ImportError:
    pass

from voicebox.tts.cache import CachedTTS, PrerecordedTTS
from voicebox.tts.espeakng import ESpeakConfig, ESpeakNG

try:
    from voicebox.tts.elevenlabs import ElevenLabs
except ImportError:
    pass

try:
    from voicebox.tts.googlecloudtts import GoogleCloudTTS
except ImportError:
    pass

try:
    from voicebox.tts.gtts import gTTS
except ImportError:
    pass

from voicebox.tts.picotts import PicoTTS


def default_tts() -> TTS:
    """Returns a new instance of the default TTS, ``PicoTTS``."""
    return PicoTTS()
