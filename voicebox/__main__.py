import argparse

from voicebox.effects.dc_offset import RemoveDcOffset
from voicebox.effects.normalize import Normalize
from voicebox.ssml import SSML
from voicebox.tts.tts import TTS
from voicebox.voicebox import Voicebox


def main():
    args = _parse_args()

    text = SSML(args.text) if args.ssml else args.text

    tts = _get_tts(args)
    effects = _get_effects(args)

    voicebox = Voicebox(tts, effects)
    voicebox.say(text)


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('text', help='Text to speak')

    # TTS args
    parser.add_argument('--tts', choices=('espeak-ng', 'googlecloudtts', 'picotts'), default='picotts',
                        help='Which TTS engine to use. Default: picotts')
    parser.add_argument('--lang', help='Language code')
    parser.add_argument('--voice', help='Voice name')
    parser.add_argument('--ssml', action='store_true', help='Treat text as SSML')
    parser.add_argument('--pitch', help='Voice pitch')
    parser.add_argument('--speed', help='Voice speed')

    # Effect args
    parser.add_argument('--scale-rate', type=float, help='Scale sample rate by this factor')
    parser.add_argument('--phaser', action='store_true', help='Add phaser effect')
    parser.add_argument('--ring-mod', action='store_true', help='Add ring modulation effect')
    parser.add_argument('--glitch', action='store_true', help='Add glitch effect')

    return parser.parse_args()


def _get_tts(args) -> TTS:
    if args.tts == 'espeak-ng':
        from voicebox.tts.espeakng import ESpeakConfig, ESpeakNG

        return ESpeakNG(ESpeakConfig(
            voice=args.voice,
            word_gap_seconds=0.0,
            pitch=int(args.pitch) if args.pitch is not None else None,
            speed=int(args.speed) if args.speed is not None else None,
        ))

    elif args.tts == 'googlecloudtts':
        from google.cloud.texttospeech import AudioConfig, TextToSpeechClient, VoiceSelectionParams
        from voicebox.tts.googlecloudtts import GoogleCloudTTS

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

    elif args.tts == 'picotts':
        from voicebox.tts.picotts import PicoTTS
        return PicoTTS(language=args.lang)

    else:
        raise ValueError(f'Unrecognized tts: {args.tts}')


def _get_effects(args):
    effects = []

    if args.scale_rate is not None:
        from voicebox.effects.samplerate import ChangeSampleRate
        effects.append(ChangeSampleRate(lambda sr: sr * args.scale_rate))

    if args.phaser:
        from voicebox.effects.delay import Delay
        effects.append(Delay(time=0.005, repeats=2))

    if args.ring_mod:
        from voicebox.effects.modulation import RingMod
        effects.append(RingMod())

    if args.glitch:
        from voicebox.effects.glitch import Glitch
        effects.append(Glitch())

    effects.extend([
        RemoveDcOffset(),
        Normalize(),
    ])

    return effects


if __name__ == '__main__':
    main()
