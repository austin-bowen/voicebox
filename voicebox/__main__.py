import argparse

from voicebox.voicebox import Voicebox


def main():
    args = _parse_args()

    voicebox = Voicebox()
    voicebox.speak(args.text)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('text', help='Text to speak')
    return parser.parse_args()


if __name__ == '__main__':
    main()
