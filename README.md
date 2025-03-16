# voicebox

![python-package](https://github.com/austin-bowen/voicebox/actions/workflows/python-package.yml/badge.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/voicebox-tts)
[![PyPI - Version](https://img.shields.io/pypi/v/voicebox-tts)](https://pypi.org/project/voicebox-tts/)
[![Documentation Status](https://readthedocs.org/projects/voicebox/badge/?version=latest)](https://voicebox.readthedocs.io/en/latest/?badge=latest)

Python text-to-speech library with built-in voice effects and support for multiple TTS engines.

| [GitHub](https://github.com/austin-bowen/voicebox/)
| [Documentation 📘](https://voicebox.readthedocs.io)
| [Audio Samples 🔉](samples)
|

```python
# Example: Use gTTS with a vocoder effect to speak in a robotic voice

from voicebox import SimpleVoicebox
from voicebox.tts import gTTS
from voicebox.effects import Vocoder, Normalize

voicebox = SimpleVoicebox(
    tts=gTTS(),
    effects=[Vocoder.build(), Normalize()],
)

voicebox.say('Hello, world! How are you today?')
```

## Setup

1. `pip install voicebox-tts`
2. Install the `PortAudio` library for audio playback.
   - On Debian/Ubuntu: `sudo apt install libportaudio2`
3. Install dependencies for whichever TTS engine(s) you want to use (see section below).

## Supported Text-to-Speech Engines

Classes for supported TTS engines are located in the
[`voicebox.tts`](voicebox.tts) package.

### Amazon Polly [🌐](https://aws.amazon.com/polly/)

Online TTS engine from AWS.

- Class: [`voicebox.tts.AmazonPolly`](voicebox.tts.amazonpolly.AmazonPolly)
- Setup: `pip install "voicebox-tts[amazon-polly]"`

### ElevenLabs [🌐](https://elevenlabs.io/)

Online TTS engine with very realistic voices and support for voice cloning.

- Class: [`voicebox.tts.ElevenLabsTTS`](voicebox.tts.elevenlabs.ElevenLabsTTS)
- Setup:
  1. `pip install "voicebox-tts[elevenlabs]"`
  2. Install ffmpeg for audio decoding.
  3. (Optional) Use an [API key](https://elevenlabs.io/docs/api-reference/authentication):
     ```python
     from elevenlabs.client import ElevenLabs
     from voicebox.tts import ElevenLabsTTS

     tts = ElevenLabsTTS(client=ElevenLabs(api_key='your-api-key'))
     ```

### eSpeak NG [🌐](https://github.com/espeak-ng/espeak-ng)

Offline TTS engine with a good number of options.

- Class: [`voicebox.tts.ESpeakNG`](voicebox.tts.espeakng.ESpeakNG)
- Setup:
  - On Debian/Ubuntu: `sudo apt install espeak-ng`

### Google Cloud Text-to-Speech [🌐](https://cloud.google.com/text-to-speech)

Powerful online TTS engine offered by Google Cloud.

- Class: [`voicebox.tts.GoogleCloudTTS`](voicebox.tts.googlecloudtts.GoogleCloudTTS)
- Setup: `pip install "voicebox-tts[google-cloud-tts]"`

### gTTS [🌐](https://github.com/pndurette/gTTS)

Online TTS engine used by Google Translate.

- Class: [`voicebox.tts.gTTS`](voicebox.tts.gtts.gTTS)
- Setup:
  1. `pip install "voicebox-tts[gtts]"`
  2. Install ffmpeg for audio decoding.

### 🤗 Parler TTS [🌐](https://github.com/huggingface/parler-tts)

Offline TTS engine released by Hugging Face that uses a promptable
deep learning model to generate speech.

- Class: [`voicebox.tts.ParlerTTS`](voicebox.tts.parlertts.ParlerTTS)
- Setup: `pip install git+https://github.com/huggingface/parler-tts.git`

### Pico TTS

Very basic offline TTS engine.

- Class: [`voicebox.tts.PicoTTS`](voicebox.tts.picotts.PicoTTS)
- Setup:
  - On Debian/Ubuntu: `sudo apt install libttspico-utils`

### pyttsx3 [🌐](https://pyttsx3.readthedocs.io/)

Offline TTS engine wrapper with support for the built-in TTS engines on Windows
(SAPI5) and macOS (NSSpeechSynthesizer), as well as espeak on Linux.
By default, it will use the most appropriate engine for your platform.

- Class: [`voicebox.tts.Pyttsx3TTS`](voicebox.tts.pyttsx3.Pyttsx3TTS)
- Setup:
  1. `pip install "voicebox-tts[pyttsx3]"`
  2. On Debian/Ubuntu: `sudo apt install espeak`

## Effects

Built-in effect classes are located in the
[`voicebox.effects`](voicebox.effects) package,
and can be imported like:

```python
from voicebox.effects import CoolEffect
```

Here is a non-exhaustive list of fun effects:
- [`Glitch`](voicebox.effects.glitch.Glitch)
  creates a glitchy sound by randomly repeating small chunks of audio.
- [`RingMod`](voicebox.effects.ring_mod.RingMod)
  can be used to create choppy, Doctor Who Dalek-like effects.
- [`Vocoder`](voicebox.effects.vocoder.Vocoder)
  is useful for making monotone, robotic voices.

There is also support for all the awesome audio plugins in
[Spotify's `pedalboard` library](https://spotify.github.io/pedalboard/index.html)
using the special [`PedalboardEffect`](voicebox.effects.pedalboard.PedalboardEffect)
wrapper, e.g.:

```python
from voicebox import SimpleVoicebox
from voicebox.effects import PedalboardEffect
import pedalboard

voicebox = SimpleVoicebox(
    effects=[
        PedalboardEffect(pedalboard.Reverb()),
        ...,
    ]
)
```

## Examples

### Minimal

```python
# PicoTTS is used to say "Hello, world!"
from voicebox import SimpleVoicebox

voicebox = SimpleVoicebox()
voicebox.say('Hello, world!')
```

### Pre-built

Some pre-built voiceboxes are available in the
[`voicebox.examples`](voicebox.examples) package.
They can be imported into your own code, and you can run them to demo:

```bash
# Voice of GLaDOS from the Portal video game series
python -m voicebox.examples.glados "optional message"

# Voice of the OOM-9 command battle droid from Star Wars: Episode I
python -m voicebox.examples.battle_droid "optional message"
```

### Advanced

```python
# Use eSpeak NG at 120 WPM and en-us voice as the TTS engine
from voicebox import reliable_tts
from voicebox.tts import ESpeakConfig, ESpeakNG, gTTS

# Wrap multiple TTSs in retries and caches
tts = reliable_tts(
    ttss=[
        # Prefer using online TTS first
        gTTS(),
        # Fall back to offline TTS if online TTS fails
        ESpeakNG(ESpeakConfig(speed=120, voice='en-us')),
    ],
)

# Add some voice effects
from voicebox.effects import Vocoder, Glitch, Normalize

effects = [
    Vocoder.build(),    # Make a robotic, monotone voice
    Glitch(),           # Randomly repeat small sections of audio
    Normalize(),        # Remove DC and make volume consistent
]

# Build audio sink
from voicebox.sinks import Distributor, SoundDevice, WaveFile

sink = Distributor([
    SoundDevice(),          # Send audio to playback device
    WaveFile('speech.wav'), # Save audio to speech.wav file
])

# Build the voicebox
from voicebox import ParallelVoicebox
from voicebox.voiceboxes.splitter import SimpleSentenceSplitter

# Parallel voicebox doesn't block the main thread
voicebox = ParallelVoicebox(
    tts,
    effects,
    sink,
    # Split text into sentences to reduce time to first speech
    text_splitter=SimpleSentenceSplitter(),
)

# Speak!
voicebox.say('Hello, world!')

# Wait for all audio to finish playing before exiting
voicebox.wait_until_done()
```

### Command Line Demo

```bash
python -m voicebox -h               # Print command help
python -m voicebox "Hello, world!"  # Basic usage
```
