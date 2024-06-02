import argparse
import sys
from typing import Iterable

from voicebox import SimpleVoicebox
from voicebox.effects import Effects
from voicebox.tts import TTS


def demo(
        description: str,
        tts: TTS,
        effects: Effects,
        default_messages: Iterable[str],
) -> None:
    args = _parse_args(description)
    messages = _get_messages(args, default_messages)

    voicebox = SimpleVoicebox(
        tts,
        effects,
    )

    voicebox.say_all(messages)


def _parse_args(description: str):
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        'message', nargs='?',
        help='Optional message to speak. If not given, then some demo lines will be spoken.',
    )

    parser.add_argument(
        '--stdin', action='store_true',
        help='Get message from stdin',
    )

    return parser.parse_args()


def _get_messages(args, default: Iterable[str]) -> Iterable[str]:
    if args.message:
        return [args.message]
    elif args.stdin:
        return [sys.stdin.read()]
    else:
        return default
