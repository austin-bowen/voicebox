# voicebox

![python-package](https://github.com/austin-bowen/voicebox/actions/workflows/python-package.yml/badge.svg)

Python text-to-speech library with built-in voice effects and support for multiple TTS engines.

## Examples

Find audio samples here: [`./samples`](./samples)

### Basic

```python
# PicoTTS is used to say "Hello, world!"
from voicebox import Voicebox
voicebox = Voicebox()
voicebox.say('Hello, world!')
```

### Advanced

```python
# Use eSpeak NG at 120 WPM and en-us voice as the TTS engine
from voicebox.tts import ESpeakConfig, ESpeakNG
tts = ESpeakNG(ESpeakConfig(speed=120, voice='en-us'))

# Add some voice effects
from voicebox.effects import Delay, Glitch, RemoveDcOffset, Normalize
effects = [
    Delay(time=0.005, repeats=2),   # A short delay makes a phaser effect
    Glitch(),                       # Randomly repeats small sections of audio
    RemoveDcOffset(),               # Just in case
    Normalize(),                    # Make volume consistent
]

# Send audio to playback device, and save to speech.wav file
from voicebox.sinks import Distributor, SoundDevice, WaveFile
sink = Distributor([
    SoundDevice(),
    WaveFile('speech.wav'),
])

# Build the voicebox
from voicebox import Voicebox
voicebox = Voicebox(tts, effects, sink)

# eSpeak NG is used to say "Hello, world!" with a phaser-y, glitched robot voice
voicebox.say('Hello, world!')
```

### Command Line Demo

```commandline
python -m voicebox -h               # Print command help
python -m voicebox "Hello, world!"  # Basic usage
```

## Setup

1. Setup virtual environment if necessary, e.g.
   1. `python3 -m venv venv`
   2. `. venv/bin/activate`
2. Install dependencies:
   1. `pip install -U pip`
   2. `pip install -r requirements/main.txt`
   3. Install the `PortAudio` library for the `sounddevice` dependency:
      - On Debian/Ubuntu: `sudo apt install libportaudio2`
   4. For development:\
      `pip install -r requirements/test.txt`
3. Install dependencies for whichever TTS engine(s) you want to use (see section below).

## Supported Text-to-Speech Engines

Classes for supported TTS engines are located in the [`voicebox.tts.*`](./voicebox/tts/) modules.

### eSpeak NG [🌐](https://github.com/espeak-ng/espeak-ng)

Offline TTS engine with a good number of options.

- Class: [`voicebox.tts.espeakng.ESpeakNG`](./voicebox/tts/espeakng.py)
- Setup:
  - On Debian/Ubuntu: `sudo apt install espeak-ng`

### Google Cloud Text-to-Speech [🌐](https://cloud.google.com/text-to-speech)

Powerful online TTS engine offered by Google Cloud.

- Class: [`voicebox.tts.googlecloudtts.GoogleCloudTTS`](./voicebox/tts/googlecloudtts.py)
- Setup: `pip install -r requirements/google-cloud-tts.txt`

### gTTS [🌐](https://github.com/pndurette/gTTS)

Online TTS engine used by Google Translate.

- Class: [`voicebox.tts.gtts.gTTS`](./voicebox/tts/gtts.py)
- Setup:
  1. `pip install -r requirements/gtts.txt`
  2. Install ffmpeg or libav for `pydub` ([docs](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up))

### Pico TTS

Very basic offline TTS engine.

- Class: [`voicebox.tts.picotts.PicoTTS`](./voicebox/tts/picotts.py)
- Setup:
  - On Debian/Ubuntu: `sudo apt install libttspico-utils`
