import argparse

from voicebox.effects.dc_offset import RemoveDcOffset
from voicebox.effects.normalize import Normalize
from voicebox.tts.picotts import PicoTTS
from voicebox.tts.tts import TTS
from voicebox.voicebox import Voicebox


def main():
    args = _parse_args()

    tts = _get_tts(args)
    effects = _get_effects(args)

    voicebox = Voicebox(tts, effects)
    voicebox.speak(args.text)


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('text', help='Text to speak')

    # TTS args
    parser.add_argument('--lang', default='en-US', help='Language code')

    # Effect args
    parser.add_argument('--scale-rate', type=float, help='Scale sample rate by this factor')
    parser.add_argument('--phaser', action='store_true', help='Add phaser effect')
    parser.add_argument('--glitch', action='store_true', help='Add glitch effect')

    return parser.parse_args()


def _get_tts(args) -> TTS:
    return PicoTTS(language=args.lang)


def _get_effects(args):
    effects = []

    if args.scale_rate is not None:
        from voicebox.effects.samplerate import ChangeSampleRate
        effects.append(ChangeSampleRate(lambda sr: sr * args.scale_rate))

    if args.phaser:
        from voicebox.effects.delay import Delay
        effects.append(Delay(time=0.005, repeats=2))

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
