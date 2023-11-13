import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Union

import nltk
import nltk.data
from nltk.tokenize.api import TokenizerI

from voicebox.ssml import SSML
from voicebox.types import KWArgs, StrOrSSML


class Splitter(ABC):
    """Splits text into chunks."""

    @abstractmethod
    def split(self, text: StrOrSSML) -> Iterable[StrOrSSML]:
        ...


class RegexSplitter(Splitter):
    """Splits text on regex pattern."""

    pattern: re.Pattern
    join_split_group: bool

    def __init__(self, pattern: Union[str, re.Pattern], join_split_group: bool = True):
        self.pattern = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        self.join_split_group = join_split_group

    def split(self, text: StrOrSSML) -> Iterable[StrOrSSML]:
        # Do not split SSML
        if isinstance(text, SSML):
            return [text]

        result = self.pattern.split(text)
        result = map(str.strip, result)
        result = filter(bool, result)

        if self.join_split_group:
            result = list(result) + ['']
            pairs = zip(result[0::2], result[1::2])
            result = (''.join(pair) for pair in pairs)

        return result


class SimpleSentenceSplitter(RegexSplitter):
    """Splits text on sentence punctuation '.', '!', and '?'."""

    def __init__(self):
        super().__init__(r'([.!?]+(?:\s+|$))')


@dataclass
class NltkTokenizerSplitter(Splitter):
    """Uses an NLTK tokenizer to split text."""

    tokenizer: TokenizerI

    def split(self, text: StrOrSSML) -> Iterable[StrOrSSML]:
        return (
            [text] if isinstance(text, SSML) else
            self.tokenizer.tokenize(text)
        )


class PunktSentenceSplitter(NltkTokenizerSplitter):
    """
    Uses the Punkt sentence tokenizer from NLTK to split text into sentences
    more intelligently than a simple pattern-based splitter. It can handle
    instances of mid-sentence punctuation very well; e.g. "Mr. Jones went to
    see Dr. Sherman" would be correctly split into only one sentence.

    This requires that the Punkt NLTK resources be located on disk,
    e.g. by downloading via one of these methods:

        >>> PunktSentenceSplitter.download_resources()

    or

        >>> import nltk; nltk.download('punkt')

    or

        $ python -m nltk.downloader punkt

    See here for all NLTK Data installation methods:
    https://www.nltk.org/data.html
    """

    def __init__(self, language: str = 'english', **kwargs):
        tokenizer = self._load_tokenizer(language, kwargs)
        super().__init__(tokenizer)

    def _load_tokenizer(self, language: str, kwargs: KWArgs) -> TokenizerI:
        return nltk.data.load(
            self._get_punkt_resource_url(language),
            **kwargs,
        )

    def _get_punkt_resource_url(self, language: str) -> str:
        return f'tokenizers/punkt/{language}.pickle'

    @staticmethod
    def download_resources(**kwargs):
        nltk.download('punkt', **kwargs)
