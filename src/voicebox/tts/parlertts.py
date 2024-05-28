from typing import Union

import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

from voicebox.audio import Audio
from voicebox.tts import TTS
from voicebox.types import StrOrSSML


class ParlerTTS(TTS):
    model: torch.nn.Module
    tokenizer: AutoTokenizer
    device: torch.device

    def __init__(
            self,
            model: torch.nn.Module,
            tokenizer: AutoTokenizer,
            device: torch.device,
            description: str,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

        self._tokenized_description = None
        self.description = description

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value
        self._tokenized_description = self._tokenize(value)

    @classmethod
    def build(
            cls,
            description: str = '',
            model_name: str = 'parler-tts/parler_tts_mini_v0.1',
            device: Union[str, torch.device] = None,
            torch_dtype: torch.dtype = None,
    ):
        if device is None:
            if torch.cuda.is_available():
                device = 'cuda:0'
            elif torch.backends.mps.is_available():
                device = 'mps'
            elif torch.xpu.is_available():
                device = 'xpu'
            else:
                device = 'cpu'
        device = torch.device(device)

        if torch_dtype is None:
            torch_dtype = torch.float16 if device.type != 'cpu' else torch.float32

        model = ParlerTTSForConditionalGeneration.from_pretrained(model_name)
        model.to(device, dtype=torch_dtype)

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        return cls(model, tokenizer, device, description)

    def get_speech(self, text: StrOrSSML) -> Audio:
        tokenized_text = self._tokenize(text)

        signal = self.model.generate(
            input_ids=self._tokenized_description,
            prompt_input_ids=tokenized_text,
        )
        signal = signal.cpu().to(torch.float32).numpy().squeeze()

        sample_rate = self.model.config.sampling_rate

        return Audio(signal, sample_rate)

    def _tokenize(self, text: str) -> torch.Tensor:
        return self.tokenizer(text, return_tensors='pt').input_ids.to(self.device)
