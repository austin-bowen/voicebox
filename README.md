# voicebox

![python-package](https://github.com/austin-bowen/voicebox/actions/workflows/python-package.yml/badge.svg)

Python text-to-speech library with built-in voice effects and support for multiple TTS engines.

## Examples

Listen to audio samples here: [Audio Samples](https://austin-bowen.github.io/voicebox/)

### Basic

```python
# PicoTTS is used to say "Hello, world!"
from voicebox import Voicebox
voicebox = Voicebox()
voicebox.say('Hello, world!')
```

### Pre-built

Some pre-built voiceboxes are available in the [`voicebox.examples`](./voicebox/examples) package.
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
from voicebox.tts import ESpeakConfig, ESpeakNG
tts = ESpeakNG(ESpeakConfig(speed=120, voice='en-us'))

# Add some voice effects
from voicebox.effects import Vocoder, Glitch, Normalize
effects = [
    Vocoder.build(),    # Makes a very robotic, monotone voice
    Glitch(),           # Randomly repeats small sections of audio
    Normalize(),        # Remove DC and make volume consistent
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

# eSpeak NG is used to say "Hello, world!" with a glitchy robot voice
voicebox.say('Hello, world!')
```

### Command Line Demo

```bash
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
   4. For development:
      - `pip install -r requirements/test.txt`
      - `python -m nltk.downloader punkt -d ./venv/nltk_data`
3. Install dependencies for whichever TTS engine(s) you want to use (see section below).

## Supported Text-to-Speech Engines

Classes for supported TTS engines are located in the [`voicebox.tts.*`](./voicebox/tts/) modules.

### Amazon Polly [🌐](https://aws.amazon.com/polly/)

Online TTS engine from AWS.

- Class: [`voicebox.tts.AmazonPolly`](./voicebox/tts/amazonpolly.py)
- Setup: `pip install -r requirements/amazon-polly.txt`

### ElevenLabs [🌐](https://elevenlabs.io/)

Online TTS engine with very realistic voices and support for voice cloning.

- Class: [`voicebox.tts.ElevenLabs`](./voicebox/tts/elevenlabs.py)
- Setup:
  1. `pip install -r requirements/elevenlabs.txt`
  2. Install ffmpeg or libav for `pydub` ([docs](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up))
  3. Get an [API key](https://elevenlabs.io/docs/api-reference/authentication)
     and do one of the following:
     - Set environment variable `ELEVEN_API_KEY=<api-key>`; or
     - Set with `import elevenlabs; elevenlabs.set_api_key('<api_key>')`; or
     - Pass as parameter to class: `voicebox.tts.ElevenLabs(api_key='<api_key>')`

### eSpeak NG [🌐](https://github.com/espeak-ng/espeak-ng)

Offline TTS engine with a good number of options.

- Class: [`voicebox.tts.ESpeakNG`](./voicebox/tts/espeakng.py)
- Setup:
  - On Debian/Ubuntu: `sudo apt install espeak-ng`

### Google Cloud Text-to-Speech [🌐](https://cloud.google.com/text-to-speech)

Powerful online TTS engine offered by Google Cloud.

- Class: [`voicebox.tts.GoogleCloudTTS`](./voicebox/tts/googlecloudtts.py)
- Setup: `pip install -r requirements/google-cloud-tts.txt`

### gTTS [🌐](https://github.com/pndurette/gTTS)

Online TTS engine used by Google Translate.

- Class: [`voicebox.tts.gTTS`](./voicebox/tts/gtts.py)
- Setup:
  1. `pip install -r requirements/gtts.txt`
  2. Install ffmpeg or libav for `pydub` ([docs](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up))

### Pico TTS

Very basic offline TTS engine.

- Class: [`voicebox.tts.PicoTTS`](./voicebox/tts/picotts.py)
- Setup:
  - On Debian/Ubuntu: `sudo apt install libttspico-utils`

## Effects

Built-in effect classes are located in the [`voicebox.effects`](./voicebox/effects/) module,
and can be imported like:

```python
from voicebox.effects import CoolEffect
```

Here is a non-exhaustive list of fun effects:
- [`Bitcrusher`](./voicebox/effects/distortion.py)
- [`Delay`](./voicebox/effects/delay.py)
- [`Flanger`](./voicebox/effects/flanger.py)
- [`Glitch`](./voicebox/effects/glitch.py)
- [`Vocoder`](./voicebox/effects/vocoder.py)

There is also support for all the awesome audio plugins in
[Spotify's `pedalboard` library](https://spotify.github.io/pedalboard/index.html)
using the special [`PedalboardEffect`](./voicebox/effects/pedalboard.py) wrapper, e.g.:

```python
from voicebox import Voicebox
from voicebox.effects import PedalboardEffect
import pedalboard

voicebox = Voicebox(
    effects=[
        PedalboardEffect(pedalboard.Reverb()),
        ...,
    ]
)
```
