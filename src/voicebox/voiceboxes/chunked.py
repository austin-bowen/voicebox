__all__ = [
    'ChunkedVoicebox',
]

from dataclasses import dataclass, field
from typing import TypeVar

from voicebox.voiceboxes.base import Voicebox, BaseVoicebox
from voicebox.voiceboxes.splitter import Splitter, default_splitter

T = TypeVar('T')
V = TypeVar('V')


@dataclass
class ChunkedVoicebox(Voicebox):
    """
    Decreases time-to-speech by splitting the message text into chunks
    (sentences by default) and saying each chunk individually.
    """

    voicebox: BaseVoicebox
    splitter: Splitter = field(default_factory=default_splitter)

    def say(self, text: str) -> None:
        for chunk in self.splitter.split(text):
            self.voicebox.say(chunk)
