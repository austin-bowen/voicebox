"""Module for constructing SSML strings."""

from typing import Union


class SSML(str):
    """A [Speech Synthesis Markup Language (SSML)](https://www.w3.org/TR/speech-synthesis/) string."""

    @classmethod
    def auto(cls, text: str) -> Union['SSML', str]:
        """
        Returns the ``text`` as SSML if it starts with ``'<speak>'``,
        otherwise returns the ``text`` unaltered.
        """

        is_ssml = text.lstrip().startswith('<speak>')
        return cls(text) if is_ssml else text
