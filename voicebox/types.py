from pathlib import Path
from typing import Union, IO

from voicebox.ssml import SSML

FileOrPath = Union[IO[bytes], str, Path]

StrOrSSML = Union[str, SSML]
