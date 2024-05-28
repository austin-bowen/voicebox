from voicebox.tts.tts import (
    TTS,
    AudioFileTTS,
    WavFileTTS,
    FallbackTTS,
    RetryTTS,
)

try:
    from voicebox.tts.tts import Mp3FileTTS
except ImportError:
    pass

try:
    from voicebox.tts.amazonpolly import AmazonPolly
except ImportError:
    pass

from voicebox.tts.cache import CachedTTS, PrerecordedTTS
from voicebox.tts.espeakng import ESpeakConfig, ESpeakNG

try:
    from voicebox.tts.elevenlabs import ElevenLabsTTS
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

try:
    from voicebox.tts.parlertts import ParlerTTS
except ImportError:
    pass

from voicebox.tts.picotts import PicoTTS

try:
    from voicebox.tts.pyttsx3 import Pyttsx3TTS
except ImportError:
    pass


def default_tts() -> TTS:
    """Returns a new instance of the default TTS, :class:`PicoTTS`."""
    return PicoTTS()
