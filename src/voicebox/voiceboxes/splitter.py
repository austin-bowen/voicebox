import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Union

import nltk
import nltk.data
from nltk.tokenize import PunktTokenizer
from nltk.tokenize.api import TokenizerI

from voicebox.ssml import SSML
from voicebox.types import StrOrSSML


class Splitter(ABC):
    """Splits text into chunks."""

    @abstractmethod
    def split(self, text: StrOrSSML) -> Iterable[StrOrSSML]:
        """
        Splits the given text into chunks, unless it is a
        :class:`voicebox.SSML` instance, in which case it is returned
        as-is, i.e. ``[text]``.
        """
        ...  # pragma: no cover


class NoopSplitter(Splitter):
    """Does not split text."""

    def split(self, text: StrOrSSML) -> Iterable[StrOrSSML]:
        yield text


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
    """
    Uses an `NLTK tokenizer <https://www.nltk.org/api/nltk.tokenize.html>`_
    to split text.
    """

    tokenizer: TokenizerI

    def split(self, text: StrOrSSML) -> Iterable[StrOrSSML]:
        return (
            [text] if isinstance(text, SSML) else
            self.tokenizer.tokenize(text)
        )


class PunktSentenceSplitter(NltkTokenizerSplitter):
    """
    Uses the `Punkt <https://www.nltk.org/api/nltk.tokenize.punkt.html>`_
    sentence tokenizer from `NLTK <https://www.nltk.org>`_ to split text into
    sentences more intelligently than a simple pattern-based splitter. It can
    handle instances of mid-sentence punctuation very well; e.g. "Mr. Jones went
    to see Dr. Sherman" would be correctly "split" into only one sentence.

    This requires that the Punkt NLTK resources be located on disk,
    e.g. by downloading via one of these methods:

        >>> PunktSentenceSplitter.download_resources()

    or

        >>> import nltk; nltk.download('punkt_tab')

    or

        $ python -m nltk.downloader punkt_tab

    See here for all NLTK Data installation methods:
    https://www.nltk.org/data.html
    """

    def __init__(self, language: str = 'english'):
        tokenizer = PunktTokenizer(language)
        super().__init__(tokenizer)

    @staticmethod
    def download_resources(**kwargs):
        """Download the Punkt NLTK resources."""
        nltk.download('punkt_tab', **kwargs)  # pragma: no cover


def default_splitter() -> Splitter:
    return NoopSplitter()
