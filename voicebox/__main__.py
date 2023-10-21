import argparse

from voicebox.effects.normalize import Normalize
from voicebox.sinks import WaveFile, SoundDevice
from voicebox.ssml import SSML
from voicebox.tts.tts import TTS
from voicebox.voicebox import Voicebox


def main():
    args = _parse_args()

    text = SSML(args.text) if args.ssml else args.text

    tts = _get_tts(args)
    effects = _get_effects(args)
    sink = _get_sink(args)

    voicebox = Voicebox(tts, effects, sink)
    voicebox.say(text)


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('text', help='Text to speak')

    # TTS args
    parser.add_argument('--tts', choices=('espeak-ng', 'googlecloudtts', 'gtts', 'picotts'), default='picotts',
                        help='Which TTS engine to use. Default: picotts')
    parser.add_argument('--lang', help='Language code')
    parser.add_argument('--voice', help='Voice name')
    parser.add_argument('--ssml', action='store_true', help='Treat text as SSML')
    parser.add_argument('--pitch', help='Voice pitch')
    parser.add_argument('--speed', help='Voice speed')

    # Effect args
    parser.add_argument('--scale-rate', type=float, help='Scale sample rate by this factor')
    parser.add_argument('--phaser', action='store_true', help='Add phaser effect')
    parser.add_argument('--flanger', action='store_true', help='Add flanger effect')
    parser.add_argument('--ring-mod', action='store_true', help='Add ring modulation effect')
    parser.add_argument('--glitch', action='store_true', help='Add glitch effect')
    parser.add_argument('--vocoder', action='store_true', help='Add vocoder effect')

    # Output
    parser.add_argument('--wave', help='Save as wave file')

    return parser.parse_args()


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
            language_code=args.lang,
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

    else:
        raise ValueError(f'Unrecognized tts: {args.tts}')


def _get_effects(args):
    effects = []

    if args.scale_rate is not None:
        from voicebox.effects import ChangeSampleRate
        effects.append(ChangeSampleRate(lambda sr: sr * args.scale_rate))

    if args.phaser:
        from voicebox.effects import Delay
        effects.append(Delay(time=0.005, repeats=2))

    if args.flanger:
        from voicebox.effects import Flanger
        effects.append(Flanger())

    if args.ring_mod:
        from voicebox.effects import RingMod
        effects.append(RingMod())

    if args.glitch:
        from voicebox.effects import Glitch
        effects.append(Glitch())

    if args.vocoder:
        from voicebox.effects import Vocoder
        effects.append(
            Vocoder.build(max_freq=5000, bands=20) if args.tts == 'picotts' else
            Vocoder.build(max_freq=10000, bands=40)
        )

    effects.append(Normalize())

    return effects


def _get_sink(args):
    return WaveFile(args.wave) if args.wave is not None else SoundDevice()


if __name__ == '__main__':
    main()
