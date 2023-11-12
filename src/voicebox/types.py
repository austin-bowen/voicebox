from pathlib import Path
from typing import Union, IO, Dict, Any

from voicebox.ssml import SSML

FileOrPath = Union[IO[bytes], str, Path]

KWArgs = Dict[str, Any]

StrOrSSML = Union[str, SSML]
