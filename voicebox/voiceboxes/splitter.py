import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Union, Dict, Any

import nltk
import nltk.data
from nltk.tokenize.api import TokenizerI

from voicebox.ssml import SSML


class Splitter(ABC):
    """Splits text into chunks."""

    @abstractmethod
    def split(self, text: str) -> Iterable[str]:
        ...


class RegexSplitter(Splitter):
    """Splits text on regex pattern."""

    pattern: re.Pattern
    join_split_group: bool

    def __init__(self, pattern: Union[str, re.Pattern], join_split_group: bool = True):
        self.pattern = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        self.join_split_group = join_split_group

    def split(self, text: str) -> Iterable[str]:
        # Do not split SSML
        if isinstance(text, SSML):
            return text

        result = self.pattern.split(text)
        result = map(str.strip, result)
        result = filter(bool, result)

        if self.join_split_group:
            result = list(result)
            pairs = zip(result[0::2], result[1::2])
            result = (''.join(pair) for pair in pairs)

        return result


class SimpleSentenceSplitter(RegexSplitter):
    """Splits text on sentence punctuation '.', '!', and '?'."""

    def __init__(self):
        super().__init__(r'([.!?]+\s+|$)')


@dataclass
class NltkTokenizerSplitter(Splitter):
    """Uses an NLTK tokenizer to split text."""

    tokenizer: TokenizerI

    def split(self, text: str) -> Iterable[str]:
        return self.tokenizer.tokenize(text)


class PunktSentenceSplitter(NltkTokenizerSplitter):
    """
    Uses the Punkt sentence tokenizer from NLTK to split text into sentences
    more intelligently than a simple pattern-based splitter. It can handle
    instances of mid-sentence punctuation very well; e.g. "Mr. Jones went to
    see Dr. Sherman" would be correctly split into only one sentence.

    Requires that the Punkt NLTK resource be located on disk, e.g. by downloading via:

    >>> import nltk; nltk.download('punkt')

    If the resource does not exist when an instance of this class is created,
    and ``download`` is set to ``True``, then this class will attempt to
    download the resource automatically using the above method.
    """

    def __init__(
            self,
            language: str = 'english',
            download: bool = False,
            download_kwargs: Dict[str, Any] = None,
            load_kwargs: Dict[str, Any] = None,
    ):
        tokenizer = self._download_and_load_tokenizer(language, download, download_kwargs, load_kwargs)
        super().__init__(tokenizer)

    def _download_and_load_tokenizer(
            self,
            language: str = 'english',
            download: bool = False,
            download_kwargs: Dict[str, Any] = None,
            load_kwargs: Dict[str, Any] = None,
    ) -> TokenizerI:
        try:
            return self._load_tokenizer(language, load_kwargs)
        except LookupError:
            if download:
                nltk.download('punkt', **(download_kwargs or {}))
                return self._load_tokenizer(language, load_kwargs)
            else:
                raise LookupError('You can fix this error by setting the constructor arg `download=True`.')

    def _load_tokenizer(self, language: str, load_kwargs: Dict[str, Any] = None) -> TokenizerI:
        return nltk.data.load(
            self._get_punkt_resource_url(language),
            **(load_kwargs or {}),
        )

    def _get_punkt_resource_url(self, language: str) -> str:
        return f'tokenizers/punkt/{language}.pickle'
