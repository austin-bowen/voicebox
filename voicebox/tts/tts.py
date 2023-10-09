from abc import ABC, abstractmethod

from voicebox.audio import Audio


class TTS(ABC):
    @abstractmethod
    def get_speech(self, text: str) -> Audio:
        ...
