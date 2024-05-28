import argparse
import sys

from voicebox import SimpleVoicebox
from voicebox.effects.normalize import Normalize
from voicebox.sinks import WaveFile, SoundDevice
from voicebox.ssml import SSML
from voicebox.tts.tts import TTS


def main():
    args = _parse_args()

    text = _get_text(args)

    tts = _get_tts(args)
    effects = _get_effects(args)
    sink = _get_sink(args)

    voicebox = SimpleVoicebox(
        tts=tts,
        effects=effects,
        sink=sink,
    )

    voicebox.say(text)


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('text', nargs='?', help='Text to speak. If not given, text is read from stdin.')

    # TTS args
    parser.add_argument(
        '--tts',
        choices=('espeak-ng', 'googlecloudtts', 'gtts', 'picotts', 'pyttsx3'),
        default='picotts',
        help='Which TTS engine to use. Default: picotts',
    )
    parser.add_argument('--lang', help='Language code')
    parser.add_argument('--voice', help='Voice name')
    parser.add_argument('--ssml', action='store_true', help='Treat text as SSML')
    parser.add_argument('--pitch', help='Voice pitch')
    parser.add_argument('--speed', help='Voice speed')

    # Effect args
    parser.add_argument('--phaser', action='store_true', help='Add phaser effect')
    parser.add_argument('--flanger', action='store_true', help='Add flanger effect')
    parser.add_argument('--ring-mod', action='store_true', help='Add ring modulation effect')
    parser.add_argument('--glitch', action='store_true', help='Add glitch effect')
    parser.add_argument('--vocoder', action='store_true', help='Add vocoder effect')

    # Output
    parser.add_argument('--wave', help='Save as wave file')

    return parser.parse_args()


def _get_text(args) -> str:
    if args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()

    text = text.strip()

    return SSML(text) if args.ssml else text


def _get_tts(args) -> TTS:
    if args.tts == 'espeak-ng':
        from voicebox.tts import ESpeakConfig, ESpeakNG

        return ESpeakNG(ESpeakConfig(
            voice=args.voice,
            word_gap_seconds=0.0,
            pitch=int(args.pitch) if args.pitch is not None else None,
            speed=int(args.speed) if args.speed is not None else None,
        ))

    elif args.tts == 'googlecloudtts':
        from google.cloud.texttospeech import AudioConfig, TextToSpeechClient, VoiceSelectionParams
        from voicebox.tts import GoogleCloudTTS

        client = TextToSpeechClient()
        voice_params = VoiceSelectionParams(
            language_code=args.lang or 'en-US',
            name=args.voice,
        )
        audio_config = AudioConfig(
            speaking_rate=float(args.speed) if args.speed is not None else None,
            pitch=float(args.pitch) if args.pitch is not None else None,
        )

        return GoogleCloudTTS(
            client,
            voice_params,
            audio_config=audio_config,
        )

    elif args.tts == 'gtts':
        from voicebox.tts import gTTS
        return gTTS(lang=args.lang) if args.lang is not None else gTTS()

    elif args.tts == 'picotts':
        from voicebox.tts import PicoTTS
        return PicoTTS(language=args.lang)

    elif args.tts == 'pyttsx3':
        from voicebox.tts import Pyttsx3TTS
        return Pyttsx3TTS()

    else:
        raise ValueError(f'Unrecognized tts: {args.tts}')


def _get_effects(args):
    effects = []

    if args.vocoder:
        from voicebox.effects import Vocoder
        effects.append(
            Vocoder.build(max_freq=5000, bands=20) if args.tts == 'picotts' else
            Vocoder.build(max_freq=10000, bands=40)
        )

    if args.ring_mod:
        from voicebox.effects import RingMod
        effects.append(RingMod())

    if args.phaser:
        from voicebox.effects import PedalboardEffect
        from pedalboard import Phaser
        effects.append(PedalboardEffect(Phaser(rate_hz=.5, centre_frequency_hz=400)))

    if args.flanger:
        from voicebox.effects import Flanger
        effects.append(Flanger())

    if args.glitch:
        from voicebox.effects import Glitch
        effects.append(Glitch())

    effects.append(Normalize())

    return effects


def _get_sink(args):
    return WaveFile(args.wave) if args.wave is not None else SoundDevice()


if __name__ == '__main__':
    main()
