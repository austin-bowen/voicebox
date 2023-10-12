# voicebox

Python text-to-speech library with built-in voice effects.

## Setup

1. Setup virtual environment, e.g.
   1. `python3 -m venv venv`
   2. `. venv/bin/activate`
2. Install dependencies:
   1. `pip install -U pip`
   2. `pip install -r requirements/main.txt`
   3. For development:\
      `pip install -r requirements/test.txt`

## Supported Text-to-Speech Engines

Classes for supported TTS engines are located in the [`voicebox.tts.*`](./voicebox/tts/) modules.

### eSpeak NG [🔗](https://github.com/espeak-ng/espeak-ng)

Offline TTS engine with a good number of options.

- Class: [`voicebox.tts.espeakng.ESpeakNG`](./voicebox/tts/espeakng.py)
- Setup:
  - On Debian/Ubuntu: `sudo apt install espeak-ng`

### Google Cloud Text-to-Speech [🔗](https://cloud.google.com/text-to-speech)

Powerful online TTS engine offered by Google Cloud.

- Class: [`voicebox.tts.googlecloudtts.GoogleCloudTTS`](./voicebox/tts/googlecloudtts.py)
- Setup: `pip install -r requirements/google-cloud-tts.txt`

### Pico TTS

Very basic offline TTS engine.

- Class: [`voicebox.tts.picotts.PicoTTS`](./voicebox/tts/picotts.py)
- Setup:
  - On Debian/Ubuntu: `sudo apt install libttspico-utils`
