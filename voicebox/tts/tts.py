from abc import ABC, abstractmethod

from voicebox.audio import Audio
from voicebox.types import StrOrSSML


class TTS(ABC):
    @abstractmethod
    def get_speech(self, text: StrOrSSML) -> Audio:
        ...
