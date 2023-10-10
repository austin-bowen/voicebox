# voicebox

Python text-to-speech library with built-in voice effects.

## Setup

1. Setup virtual environment, e.g.
   1. `python3 -m venv venv`
   2. `. venv/bin/activate`
2. Install dependencies:
   1. `pip install -U pip`
   2. `pip install -r requirements.txt`
   3. For development:\
      `pip install -r requirements.test.txt`

## Supported Text-to-Speech Engines

### [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech)
- Class: [`GoogleCloudTTS`](./voicebox/tts/googlecloudtts.py)
- Setup: `pip install -r requirements.google-cloud-tts.txt`

### Pico TTS
- Class: [`PicoTTS`](./voicebox/tts/picotts.py)
- Setup:
  - On Debian/Ubuntu: `apt install libttspico-utils`
