from pathlib import Path
from typing import Union, IO

FileOrPath = Union[IO[bytes], str, Path]


class SSML(str):
    """A [Speech Synthesis Markup Language (SSML)](https://www.w3.org/TR/speech-synthesis/) string."""


StrOrSSML = Union[str, SSML]
